# download_all_bge.py
from huggingface_hub import snapshot_download, list_repo_files
import os
import shutil
from pathlib import Path

# ================== 配置区 ==================
# 模型列表（Hugging Face 官方路径）
MODELS = [
    "BAAI/bge-small-zh-v1.5",
    # "BAAI/bge-base-zh-v1.5",
    "BAAI/bge-large-zh-v1.5",
    # "BAAI/bge-small-en-v1.5",
    # "BAAI/bge-base-en-v1.5",
    # "BAAI/bge-large-en-v1.5",
    # "BAAI/bge-m3",
]

# 本地保存根目录
LOCAL_BASE = "./models"

# 必须存在的核心文件（用于判断模型是否完整）
REQUIRED_FILES = ["config.json", "tokenizer.json", "pytorch_model.bin"]

# ===========================================

os.makedirs(LOCAL_BASE, exist_ok=True)

def is_model_complete(local_dir: str) -> bool:
    """检查本地模型是否包含所有必需文件"""
    if not Path(local_dir).exists():
        return False
    missing = [f for f in REQUIRED_FILES if not (Path(local_dir) / f).exists()]
    if missing:
        print(f"  缺少文件: {missing}")
        return False
    return True

def should_skip(repo_id: str, local_dir: str) -> bool:
    """判断是否跳过下载"""
    if is_model_complete(local_dir):
        print(f"  模型已完整存在，跳过下载")
        return True
    else:
        if Path(local_dir).exists():
            print(f"  模型目录存在但不完整，将重新下载")
            shutil.rmtree(local_dir)  # 删除残缺目录
        return False

print("开始智能批量下载 BAAI BGE 模型（跳过已完整模型）...\n")
print(f"保存目录: {os.path.abspath(LOCAL_BASE)}\n")
print("=" * 70)

for repo_id in MODELS:
    model_name = repo_id.split("/")[-1]
    local_dir = os.path.join(LOCAL_BASE, model_name)
    
    print(f"检查模型: {repo_id}")
    print(f"  本地路径: {local_dir}")

    # 步骤1：本地完整性检测
    if should_skip(repo_id, local_dir):
        print(f"  跳过 {repo_id}\n")
        continue

    # 步骤2：下载
    print(f"  正在下载（支持断点续传）...")
    try:
        snapshot_download(
            repo_id=repo_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
            # tqdm_class=None,  # 保留默认进度条
        )
        print(f"  下载完成！\n")
    except Exception as e:
        print(f"  下载失败: {e}\n")
        continue

print("=" * 70)
print("所有任务完成！")
print("\n可用模型路径：")
for model in MODELS:
    name = model.split("/")[-1]
    path = f"./models/{name}"
    status = "完整" if is_model_complete(path) else "缺失"
    print(f"  {name}: {path} [{status}]")