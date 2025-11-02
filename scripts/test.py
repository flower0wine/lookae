import asyncio
from core.utils import find_files
from pathlib import Path


OUTPUT_DIR = "outputs"

async def main():
    file_path_list = find_files("data", "*.md")
    
    count = 0
    s = set()
    for fp in file_path_list:
        count += 1
        stem = Path(fp).stem
        out_path = Path(OUTPUT_DIR) / f"{stem}.json"
        s.add(stem)
        if out_path.exists():
            continue
        else:
            print(str(out_path))
            
    print(count)
    print(len(list(s)))
    
if __name__ == "__main__":
    asyncio.run(main())