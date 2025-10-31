import asyncio
import json
from langchain.utils import find_files, read_file_async

async def main():
    # 定义必需的字段
    required_fields = {
        'title', 'slug', 'author', 'post_date', 'source_url', 
        'category', 'tags', 'content', 'image_urls', 'video_urls',
        'supported_versions', 'supported_os', 'download_links', 'other'
    }
    
    # 查找所有 JSON 文件
    file_path_list = find_files("outputs", "*.json")
    
    invalid_files = []
    
    for file_path in file_path_list:
        try:
            # 读取文件内容
            success, content, error = await read_file_async(str(file_path))
            
            if not success:
                invalid_files.append({
                    'file': str(file_path),
                    'error': f'读取文件失败: {error}'
                })
                continue
            
            # 尝试解析 JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                invalid_files.append({
                    'file': str(file_path),
                    'error': f'JSON 格式错误: {str(e)}'
                })
                continue
            
            # 检查是否为字典类型
            if not isinstance(data, dict):
                invalid_files.append({
                    'file': str(file_path),
                    'error': 'JSON 根节点不是对象类型'
                })
                continue
            
            # 检查必需字段
            missing_fields = required_fields - set(data.keys())
            if missing_fields:
                invalid_files.append({
                    'file': str(file_path),
                    'error': f'缺少必需字段: {", ".join(sorted(missing_fields))}'
                })
                
        except Exception as e:
            invalid_files.append({
                'file': str(file_path),
                'error': f'处理文件时发生异常: {str(e)}'
            })
    
    # 输出结果
    if invalid_files:
        print("发现以下不符合要求的文件:")
        print("=" * 60)
        for item in invalid_files:
            print(f"文件: {item['file']}")
            print(f"错误: {item['error']}")
            print("-" * 40)
        print(f"\n总计: {len(invalid_files)} 个文件不符合要求")
    else:
        print("所有文件都符合要求！")
    
    return invalid_files

if __name__ == "__main__":
    asyncio.run(main())
