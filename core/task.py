from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# Async logger and LLM client are guaranteed installed per project spec
import logging
from litellm import acompletion
import sys
from langchain.model_pool import get_model

logger = logging.getLogger()


# -------------------------------
# Data structures
# -------------------------------

@dataclass
class TaskSpec:
    model: str
    messages: Sequence[Dict[str, Any]]
    # Optional file name to save parsed JSON; if None, will be auto-generated
    output_filename: Optional[str] = None
    # Optional metadata for tracing
    meta: Optional[Dict[str, Any]] = None


@dataclass
class TaskResult:
    model: str
    ok: bool
    # Raw response from the provider (dict) if available
    response: Optional[Dict[str, Any]]
    # Parsed JSON (dict) if parsing succeeded
    parsed: Optional[Dict[str, Any]]
    # Output file path if saved
    output_path: Optional[Path]
    # Error text if failed
    error: Optional[str]
    # Retry count used
    retries: int = 0
    # Extra metadata
    meta: Optional[Dict[str, Any]] = None


# -------------------------------
# Helpers
# -------------------------------

_DEFAULT_JSON_REGEX = re.compile(r"```json\s*(\{[\s\S]*?\})\s*```|\{[\s\S]*\}", re.IGNORECASE)


def _extract_json_text(text: str, pattern: Optional[re.Pattern] = None) -> Optional[str]:
    if not text:
        return None
    pat = pattern or _DEFAULT_JSON_REGEX
    m = pat.search(text)
    if not m:
        return None
    # Prefer first capturing group if present
    if m.lastindex:
        return m.group(1)
    return m.group(0)


def _safe_json_loads(s: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(s)
    except Exception:
        # Try to relax common formatting issues
        s2 = s.strip()
        try:
            return json.loads(s2)
        except Exception:
            return None


async def _save_json_async(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    # Avoid external deps; write in a thread
    def _write():
        with open(path, "w", encoding="utf-8") as f:
            f.write(payload)

    await asyncio.to_thread(_write)


def _make_output_filename(model: str, index: int, suffix: str = ".json") -> str:
    safe_model = model.replace("/", "-").replace(":", "-")
    ts = int(time.time())
    return f"{index:03d}_{safe_model}_{ts}{suffix}"


async def _invoke_with_retries(
    task: TaskSpec,
    timeout: int,
    max_retries: int,
    json_regex: Optional[re.Pattern],
    output_dir: Path,
    index: int,
) -> TaskResult:
    attempts = 0
    last_error: Optional[str] = None
    last_response: Optional[Dict[str, Any]] = None
    parsed_json: Optional[Dict[str, Any]] = None
    output_path: Optional[Path] = None
    # track the model used for the current attempt (may change across retries)
    current_model: str = task.model

    while attempts <= max_retries:
        try:
            attempts += 1
            logger.info(
                f"Starting task for model={current_model}, attempt={attempts}/{max_retries + 1}"
            )

            coro = acompletion(model=current_model, messages=list(task.messages))
            resp: Dict[str, Any] = await asyncio.wait_for(coro, timeout=timeout)
            last_response = resp

            # check provider-level success; require choices[0].message.content
            choices = resp.get("choices")
            text = None
            if isinstance(choices, list) and choices:
                text = (choices[0] or {}).get("message", {}).get("content")
            if not text:
                # non-successful response though request returned; try switching model if retries left
                # attempt to extract error info if present
                err_block = resp.get("error") or resp.get("status") or {}
                err_code = None
                err_msg = None
                if isinstance(err_block, dict):
                    err_code = err_block.get("code") or err_block.get("status_code")
                    err_msg = err_block.get("message") or err_block.get("msg")
                last_error = (
                    f"Non-success response: code={err_code} message={err_msg}"
                    if (err_code or err_msg)
                    else "Non-success response: missing choices/content"
                )
                logger.warning(
                    f"Model={current_model} attempt={attempts} got non-success response; {last_error}"
                )
                if attempts <= max_retries:
                    # switch model from pool and retry
                    try:
                        new_model = await get_model()
                        logger.info(
                            f"Switching model for retry: {current_model} -> {new_model} (attempt {attempts+1}/{max_retries+1})"
                        )
                        current_model = new_model
                    except Exception as e:  # noqa: BLE001
                        logger.warning(f"Failed to get model from pool: {e}")
                    # backoff before next attempt
                    await asyncio.sleep(min(2 ** (attempts - 1), 5))
                    continue
                else:
                    raise RuntimeError(last_error)

            json_text = _extract_json_text(text, json_regex)
            if not json_text:
                raise RuntimeError("Failed to locate JSON in response")

            parsed = _safe_json_loads(json_text)
            if parsed is None:
                raise RuntimeError("Failed to parse JSON text")

            # Save
            filename = task.output_filename or _make_output_filename(current_model, index)
            output_path = (output_dir / filename).resolve()
            await _save_json_async(output_path, parsed)

            parsed_json = parsed
            return TaskResult(
                model=current_model,
                ok=True,
                response=last_response,
                parsed=parsed_json,
                output_path=output_path,
                error=None,
                retries=attempts - 1,
                meta=task.meta,
            )

        except asyncio.TimeoutError:
            last_error = f"Timeout after {timeout}s"
            logger.warning(
                f"Timeout model={task.model} attempt={attempts}: {last_error}"
            )
        except Exception as e:  # noqa: BLE001
            last_error = str(e)
            logger.warning(
                f"Error model={current_model} attempt={attempts}: {last_error}"
            )

        # simple backoff
        if attempts <= max_retries:
            await asyncio.sleep(min(2 ** (attempts - 1), 5))

    # Final failure
    return TaskResult(
        model=current_model,
        ok=False,
        response=last_response,
        parsed=None,
        output_path=output_path,
        error=last_error or "Unknown error",
        retries=attempts - 1,
        meta=task.meta,
    )


async def run_tasks_parallel(
    tasks: Sequence[TaskSpec],
    *,
    timeout: int = 60,
    max_retries: int = 100000,
    output_dir: str | Path = "outputs",
    json_regex: Optional[re.Pattern] = None,
) -> List[TaskResult]:
    """Run per-task model calls in parallel with concurrency and retries.

    Each TaskSpec contains its own messages and model. For each response, we
    try to extract a JSON object via regex, parse it, and save it to output_dir.

    Returns a list of TaskResult in the same order as the input tasks.
    """
    out_dir = Path(output_dir)
    logger.info(
        f"Starting run_tasks_parallel: tasks={len(tasks)}, timeout={timeout}, max_retries={max_retries}, output_dir={out_dir}"
    )

    # Note: sequential async execution (no concurrency) for maintainability and stability
    results: List[Optional[TaskResult]] = [None] * len(tasks)

    # Total-time ticker displayed at the bottom and updated periodically
    start_total = time.perf_counter()
    done_event = asyncio.Event()

    async def _ticker() -> None:
        # Update every 0.5s
        while not done_event.is_set():
            elapsed = time.perf_counter() - start_total
            # Print on the same line to act as a dynamic footer
            sys.stdout.write(f"\rTotal elapsed: {elapsed:.1f}s")
            sys.stdout.flush()
            try:
                await asyncio.wait_for(done_event.wait(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
        sys.stdout.write("\n")
        sys.stdout.flush()

    # Run ticker concurrently with the tasks
    ticker_task = asyncio.create_task(_ticker())
    
    async def _run_one(i: int, t: TaskSpec) -> TaskResult:
        start_ts = time.perf_counter()
        res = await _invoke_with_retries(
            t, timeout=timeout, max_retries=max_retries, json_regex=json_regex, output_dir=out_dir, index=i
        )
        duration_s = time.perf_counter() - start_ts
        results[i] = res
        # Log execution time and outcome for this task
        if res.ok:
            logger.info(
                f"Task finished index={i} model={res.model} status=success "
                f"retries={res.retries} saved={res.output_path} duration={duration_s:.3f}s"
            )
        else:
            logger.error(
                f"Task finished index={i} model={res.model} status=fail "
                f"retries={res.retries} error={res.error} duration={duration_s:.3f}s"
            )
        return res
    try:
        coros = [_run_one(i, t) for i, t in enumerate(tasks)]
        await asyncio.gather(*coros)

    finally:
        # Stop ticker, print final line with newline
        done_event.set()
        await ticker_task
        final_elapsed = time.perf_counter() - start_total
        sys.stdout.write(f"\rTotal elapsed: {final_elapsed:.1f}s\n")
        sys.stdout.flush()

    # type: ignore[return-value]
    return [r for r in results if r is not None]

