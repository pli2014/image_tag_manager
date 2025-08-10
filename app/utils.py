import os
import json
import re
import hashlib
from typing import Dict, List
from config import CACHE_FILE, IMAGE_DIRECTORIES
from urllib.parse import quote


def get_cache_data() -> Dict:
    """
    获取缓存数据
    
    Returns:
        Dict: 缓存数据字典
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def calculate_total_tokens(cache_data: Dict) -> int:
    """
    计算总token使用量
    
    Args:
        cache_data (Dict): 缓存数据
        
    Returns:
        int: 总token数
    """
    total = 0
    for item in cache_data.values():
        total += item.get("token_usage", {}).get("total_tokens", 0)
    return total


def extract_tags(cache_data: Dict) -> List[str]:
    """
    从缓存数据中提取所有标签
    
    Args:
        cache_data (Dict): 缓存数据
        
    Returns:
        List[str]: 标签列表
    """
    tags = set()
    for data in cache_data.values():
        labels = data.get("labels", "")
        # 确保labels是字符串类型
        if not isinstance(labels, str):
            labels = str(labels)
        # 使用正则表达式提取可能的标签（中文词汇）
        extracted_tags = re.findall(r'[\u4e00-\u9fff]+', labels)
        tags.update(extracted_tags)
    return sorted(list(tags))


def simplify_labels(labels) -> str:
    """
    简化标签内容
    
    Args:
        labels: 标签内容，可以是字符串、列表或其他类型
        
    Returns:
        str: 简化后的标签字符串
    """
    # 如果labels是列表，先转换为字符串
    if isinstance(labels, list):
        # 确保列表中的所有元素都是字符串
        labels = ', '.join(str(item) for item in labels)
    # 确保labels是字符串类型
    if not isinstance(labels, str):
        labels = str(labels)
    # 移除多余的空白字符和换行符
    labels = re.sub(r'\s+', ' ', labels.strip())
    # 如果标签太长，截取前100个字符
    return labels[:100] + "..." if len(labels) > 100 else labels


def generate_md5_path(image_path: str) -> str:
    """
    为图片生成MD5索引路径
    
    Args:
        image_path (str): 图片的真实路径
        
    Returns:
        str: MD5索引路径
    """
    # 获取文件扩展名
    _, ext = os.path.splitext(image_path)
    # 生成文件路径的MD5值
    md5_hash = hashlib.md5(image_path.encode('utf-8')).hexdigest()
    # 返回MD5路径（保持原始扩展名）
    return f"{md5_hash}{ext}"


def get_image_url(image_path: str, cache_data: Dict = None) -> str:
    """
    获取图片的URL路径
    
    Args:
        image_path (str): 图片路径
        cache_data (Dict, optional): 缓存数据，用于查找MD5路径映射
        
    Returns:
        str: 图片URL
    """
    # 如果提供了缓存数据，尝试查找MD5路径映射
    if cache_data:
        # 在缓存中查找该图片路径对应的MD5路径
        image_info = cache_data.get(image_path)
        if image_info and "md5_path" in image_info:
            return f"/assets/{quote(image_info['md5_path'])}"
    
    # 如果没有缓存数据或未找到映射，使用传统方法
    # 遍历所有配置的图片目录，找到匹配的目录
    for image_directory in IMAGE_DIRECTORIES:
        try:
            # 尝试计算相对于当前目录的路径
            rel_path = os.path.relpath(image_path, image_directory)
            # 检查是否成功计算出相对路径（如果不是子路径，relpath会返回'..'开头的路径）
            if not rel_path.startswith('..'):
                # 确保路径分隔符统一为正斜杠
                rel_path = rel_path.replace(os.sep, '/')
                return f"/assets/{quote(rel_path)}"
        except ValueError:
            # 如果无法计算相对路径，继续尝试下一个目录
            continue
    
    # 如果在所有目录中都找不到匹配项，使用文件名
    return f"/assets/{quote(os.path.basename(image_path))}"