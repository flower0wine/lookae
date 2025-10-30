from typing import List, Union, Pattern, Generator, Tuple, Optional
import os
import aiofiles
import fnmatch
import re
import pathlib


async def read_file_async(
    file_path: str,
    encoding: str = 'utf-8',
    errors: str = 'ignore'
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    异步安全读取文件内容
    Args:
        file_path (str): 文件路径
        encoding (str): 文件编码，默认为 'utf-8'
        errors (str): 编码错误处理方式，'ignore' 或 'replace'，默认为 'ignore'

    Returns:
        (success: bool, content: str|None, error: str|None)
    """
    # 1. 路径检查（同步但轻量）
    if not file_path or not isinstance(file_path, str):
        return False, None, "文件路径不能为空或必须是字符串"

    if not os.path.exists(file_path):
        return False, None, f"文件不存在: {file_path}"

    if not os.path.isfile(file_path):
        return False, None, f"路径不是文件: {file_path}"

    try:
        async with aiofiles.open(file_path, 'r', encoding=encoding, errors=errors) as f:
            content = await f.read()
        return True, content, None

    except PermissionError:
        return False, None, f"权限不足: {file_path}"
    except UnicodeDecodeError as e:
        return False, None, f"编码错误（encoding='{encoding}'）: {e}"
    except OSError as e:
        return False, None, f"系统错误: {e}"
    except Exception as e:
        return False, None, f"未知错误: {type(e).__name__}: {e}"


def find_files(
    root: Union[str, pathlib.Path],
    pattern: str = "*",
    *,
    ignore_patterns: Union[str, List[str], None] = None,
    ignore_dirs: Union[str, List[str], None] = None,
    regex_filter: Union[str, Pattern, None] = None,
    follow_symlinks: bool = False,
    include_dirs: bool = False,
    errors: str = "warn",  # "ignore", "warn", "raise"
    yield_generator: bool = True,
) -> Union[Generator[pathlib.Path, None, None], List[pathlib.Path]]:
    """
    递归查找文件路径（支持通配符、正则、忽略规则）

    参数:
        root: 起始目录路径
        pattern: 通配符模式，默认为 "*"（所有文件）
                  支持 glob 风格，如 "*.py", "src/**/*.txt"
        ignore_patterns: 文件名/路径的忽略通配符列表，如 [".*","__pycache__"]
        ignore_dirs: 目录名的忽略通配符列表，如 ["node_modules", ".git"]
        regex_filter: 正则表达式（str 或 compiled Pattern），进一步过滤路径
        follow_symlinks: 是否跟随符号链接（注意：可能导致循环）
        include_dirs: 是否包含目录（默认只返回文件）
        errors: 遇到权限错误时的行为
                - "ignore": 静默忽略
                - "warn": 打印警告
                - "raise": 抛出异常
        yield_generator: True 返回生成器，False 返回完整列表

    返回:
        生成器或列表，包含 pathlib.Path 对象
    """
    def _normalize_list(obj) -> List[str]:
        if obj is None:
            return []
        return [obj] if isinstance(obj, str) else list(obj)

    root_path = pathlib.Path(root).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"Root path is not a directory: {root}")

    # 编译正则
    regex_obj = re.compile(regex_filter) if isinstance(regex_filter, str) else regex_filter

    # 标准化忽略规则
    ignore_patterns = _normalize_list(ignore_patterns) or []
    ignore_dirs = _normalize_list(ignore_dirs) or []

    # 添加默认忽略（可选）
    default_ignore_dirs = {'.git', '.svn', '__pycache__', 'node_modules', '.venv', 'venv', '.env'}
    ignore_dirs = list(set(ignore_dirs) | default_ignore_dirs)

    def _should_ignore(path: pathlib.Path, is_dir: bool) -> bool:
        name = path.name

        # 忽略目录匹配
        if is_dir and any(fnmatch.fnmatch(name, pat) for pat in ignore_dirs):
            return True

        # 忽略文件匹配
        if not is_dir and any(fnmatch.fnmatch(name, pat) for pat in ignore_patterns):
            return True

        # 隐藏文件（可选）
        if name.startswith('.'):
            return True

        return False

    def _match_pattern(path: pathlib.Path) -> bool:
        # 支持 ** 通配符（递归目录）
        if '**' in pattern:
            try:
                return path.match(pattern)
            except Exception:
                return fnmatch.fnmatch(path.name, pattern.split('/')[-1])
        else:
            return fnmatch.fnmatch(path.name, pattern)

    def _match_regex(path: pathlib.Path) -> bool:
        if regex_obj is None:
            return True
        return bool(regex_obj.search(str(path)))

    def _walk() -> Generator[pathlib.Path, None, None]:
        stack = [root_path]

        while stack:
            current_dir = stack.pop()

            try:
                with os.scandir(current_dir) as entries:
                    for entry in entries:
                        try:
                            path = pathlib.Path(entry.path)

                            # 解析符号链接
                            if entry.is_symlink():
                                if not follow_symlinks:
                                    continue
                                try:
                                    path = path.resolve()
                                    if path in {p.resolve() for p in stack}:  # 防止循环
                                        continue
                                except (OSError, RuntimeError):
                                    continue

                            is_dir = entry.is_dir(follow_symlinks=follow_symlinks)

                            if _should_ignore(path, is_dir):
                                continue

                            if is_dir:
                                if include_dirs and _match_pattern(path) and _match_regex(path):
                                    yield path
                                stack.append(path)
                            else:
                                if _match_pattern(path) and _match_regex(path):
                                    yield path

                        except (PermissionError, OSError) as e:
                            _handle_error(e, entry.path)

            except (PermissionError, OSError) as e:
                _handle_error(e, str(current_dir))
                continue

    def _handle_error(exc: Exception, path: str):
        if errors == "raise":
            raise
        elif errors == "warn":
            print(f"[WARNING] 跳过不可访问路径: {path} ({exc.__class__.__name__})")

    result = _walk()
    return result if yield_generator else list(result)


