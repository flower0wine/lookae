import litellm
from dotenv import load_dotenv
from langchain.user_prompt import get_use_prompt
from langchain.utils import read_file_async, find_files
import asyncio
from langchain.task import run_tasks_parallel, TaskSpec
from pathlib import Path

load_dotenv()

# Optional: enable litellm debug for diagnostics
litellm._turn_on_debug()

MODEL = "dashscope/qwen3-max"
OUTPUT_DIR = "outputs"

async def main():
    file_path_list = find_files("data", "*.md")

    tasks = []
    count = 0
    for fp in file_path_list:
        ok, content, err = await read_file_async(str(fp))
        if err:
            print(f"read error: {fp} -> {err}")
            continue
        messages = [{"role": "user", "content": get_use_prompt(content=content)}]
        # One message -> one model execution (no multi-model fan-out)
        tasks.append(TaskSpec(
            model=MODEL,
            messages=messages,
            # Optional: name output by input filename
            output_filename=f"{Path(fp).stem}.json",
            meta={"source": str(fp)}
        ))
        if count == 3:
            break
        count += 1

    if not tasks:
        print("no tasks to run")
        return

    results = await run_tasks_parallel(
        tasks,
        concurrency=3,
        timeout=60,
        max_retries=1,
        output_dir=OUTPUT_DIR,
    )

    ok_cnt = sum(1 for r in results if r.ok)
    print(f"completed: {ok_cnt}/{len(results)} ok; outputs in: {OUTPUT_DIR}")
    for r in results:
        if r.ok:
            print(f"OK  | {r.meta.get('source')} -> {r.output_path}")
        else:
            print(f"ERR | {r.meta.get('source')} -> {r.error}")

if __name__ == "__main__":
    asyncio.run(main())