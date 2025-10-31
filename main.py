import litellm
from dotenv import load_dotenv
from langchain.user_prompt import get_use_prompt
from langchain.utils import read_file_async, find_files
import asyncio
from langchain.task import run_tasks_parallel, TaskSpec
from langchain.model_pool import get_model

from pathlib import Path

import logging, sys
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.StreamHandler(sys.stdout)], force=True)

logger = logging.getLogger()

load_dotenv()

# Optional: enable litellm debug for diagnostics
# litellm._turn_on_debug()


OUTPUT_DIR = "outputs"

async def main():
    file_path_list = find_files("data", "*.md")

    tasks = []
    count = 0
    for fp in file_path_list:
        # Scheme A: skip if output already exists
        stem = Path(fp).stem
        out_path = Path(OUTPUT_DIR) / f"{stem}.json"
        if out_path.exists():
            # logger.info(f"skip existed: {fp} -> {out_path}")
            continue

        ok, content, err = await read_file_async(str(fp))
        if not ok:
            print(f"read error: {fp} -> {err}")
            continue
        messages = [{"role": "user", "content": get_use_prompt(content=content)}]
        # One message -> one model execution (no multi-model fan-out)
        # pick a model from the pool in round-robin manner
        model_name = await get_model()
        tasks.append(TaskSpec(
            model=model_name,
            messages=messages,
            output_filename=f"{Path(fp).stem}.json",
            meta={"source": str(fp)}
        ))

        # if count == 0:
        #     break
        # count += 1

    if not tasks:
        print("no tasks to run")
        return

    results = await run_tasks_parallel(
        tasks,
        timeout=60,
        output_dir=OUTPUT_DIR,
    )

    ok_cnt = sum(1 for r in results if r.ok)
    logger.info(f"completed: {ok_cnt}/{len(results)} ok; outputs in: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())