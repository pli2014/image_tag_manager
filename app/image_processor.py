import os
import json
import logging
from typing import Dict, List, Tuple
from config import IMAGE_DIRECTORIES, CACHE_FILE, SUPPORTED_FORMATS
from utils import get_cache_data, generate_md5_path
from dashscope import MultiModalConversation
import dashscope
from config import DASHSCOPE_API_KEY

# 设置API密钥
dashscope.api_key = DASHSCOPE_API_KEY

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_images_from_directories(directories: List[str]) -> List[str]:
    """
    从多个目录收集图片文件路径
    
    Args:
        directories (List[str]): 目录路径列表
        
    Returns:
        List[str]: 图片文件路径列表
    """
    image_paths = []
    for directory in directories:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(SUPPORTED_FORMATS):
                        image_path = os.path.join(root, file)
                        image_paths.append(image_path)
    return image_paths


def process_single_image(image_path: str) -> Dict:
    """
    处理单张图片，获取标签信息
    
    Args:
        image_path (str): 图片路径
        
    Returns:
        Dict: 包含标签和token使用量的信息
    """
    try:
        # 构造提示词
        prompt = "请识别这张图片中的内容，包括人物、物体、颜色、服饰等元素，并以简洁的方式列出5个以内的关键词，严格控制格式，空格隔开,例如：风景 女孩 蓝色裙子"
        
        # 调用通义千问VL Max模型
        messages = [
            {
                "role": "user",
                "content": [
                    {"image": f"file://{image_path}"},
                    {"text": prompt}
                ]
            }
        ]
        
        # 记录输入日志
        logger.info(f"模型调用输入 - 图片路径: {image_path}")
        logger.info(f"模型调用输入 - 提示词: {prompt}")
        
        response = MultiModalConversation.call(
            model='qwen-vl-max',
            messages=messages
        )
        
        # 记录输出日志
        logger.info(f"模型调用输出 - 状态码: {response.status_code}")
        logger.info(f"模型调用输出 - 响应: {response}")
        
        # 解析响应
        if response.status_code == 200:
            output = response.output
            
            # 安全地获取token使用情况
            token_usage = {}
            if hasattr(response, 'usage'):
                token_usage = response.usage
            elif hasattr(output, 'usage'):
                token_usage = output.usage
            else:
                token_usage = {}
            
            # 正确解析响应内容
            labels = "无法解析响应内容"
            if hasattr(output, 'choices') and len(output.choices) > 0:
                message = output.choices[0].message
                if hasattr(message, 'content'):
                    content = message.content
                    # 根据content的类型处理
                    if isinstance(content, list) and len(content) > 0:
                        # content是列表形式
                        first_item = content[0]
                        if isinstance(first_item, dict):
                            if 'text' in first_item:
                                labels = first_item['text']
                            else:
                                labels = str(content)
                        else:
                            labels = str(content)
                    elif isinstance(content, str):
                        # content是字符串形式
                        labels = content
                    else:
                        labels = str(content)
                else:
                    labels = "响应内容为空"
            else:
                labels = "响应中无选择内容"
            
            logger.info(f"成功处理图片: {image_path}, 标签: {labels}")
            
            # 生成MD5路径
            md5_path = generate_md5_path(image_path)
            
            return {
                "labels": labels,
                "token_usage": token_usage,
                "md5_path": md5_path,
                "real_path": image_path
            }
        else:
            error_msg = f"处理失败: {response.message}"
            logger.error(f"处理图片失败: {image_path}, 错误: {error_msg}")
            # 生成MD5路径
            md5_path = generate_md5_path(image_path)
            return {
                "labels": error_msg,
                "token_usage": {},
                "md5_path": md5_path,
                "real_path": image_path
            }
    except Exception as e:
        error_msg = f"处理异常: {str(e)}"
        logger.error(f"处理图片异常: {image_path}, 异常: {error_msg}")
        # 生成MD5路径
        md5_path = generate_md5_path(image_path)
        return {
            "labels": error_msg,
            "token_usage": {},
            "md5_path": md5_path,
            "real_path": image_path
        }


def process_images(directories: List[str] = None, incremental: bool = True) -> Dict:
    """
    处理图片目录中的所有图片
    
    Args:
        directories (List[str], optional): 图片目录列表，默认使用配置中的IMAGE_DIRECTORIES
        incremental (bool): 是否增量处理，True表示只处理未处理过的图片，False表示全量处理
        
    Returns:
        Dict: 处理结果，包括处理的图片数量、token消耗和缓存数据
    """
    # 如果没有提供目录，则使用配置中的目录
    if directories is None:
        directories = IMAGE_DIRECTORIES
    
    # 获取现有缓存数据
    cache = get_cache_data() if incremental else {}
    
    # 收集所有图片路径
    image_paths = collect_images_from_directories(directories)
    
    # 统计信息
    processed_count = 0
    total_tokens = 0
    
    # 处理每张图片
    for image_path in image_paths:
        # 如果是增量处理且图片已处理过，则跳过
        if incremental and image_path in cache:
            total_tokens += cache[image_path].get("token_usage", {}).get("total_tokens", 0)
            continue
        
        # 处理图片
        result = process_single_image(image_path)
        
        # 更新缓存
        cache[image_path] = result
        
        # 更新统计信息
        processed_count += 1
        total_tokens += result.get("token_usage", {}).get("total_tokens", 0)
    
    # 保存缓存
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    
    logger.info(f"处理完成 - 处理图片数: {processed_count}, 总token消耗: {total_tokens}")
    
    return {
        "processed_count": processed_count,
        "total_tokens": total_tokens,
        "cache": cache
    }


def load_cache() -> Dict:
    """
    加载缓存数据
    
    Returns:
        Dict: 缓存数据
    """
    return get_cache_data()