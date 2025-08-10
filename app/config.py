import os

# 图片目录配置 - 支持多个目录
# 可以通过逗号分隔指定多个目录，或者使用环境变量 IMAGE_DIRECTORIES
IMAGE_DIRECTORIES_ENV = os.getenv("IMAGE_DIRECTORIES", "")
if IMAGE_DIRECTORIES_ENV:
    IMAGE_DIRECTORIES = [d.strip() for d in IMAGE_DIRECTORIES_ENV.split(",") if d.strip()]
else:
    # 默认图片目录
    IMAGE_DIRECTORIES = [os.getenv("IMAGE_DIRECTORY", "D:\\workspace\\qwen_proj\\images")]

# 为了保持向后兼容，仍然保留单个目录的配置
IMAGE_DIRECTORY = IMAGE_DIRECTORIES[0] if IMAGE_DIRECTORIES else "D:\\workspace\\qwen_proj\\images"

# 阿里云百炼配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-71958a6349f24ae1ac030799553b3778")

# 缓存文件路径
CACHE_FILE = os.getenv("CACHE_FILE", "./cache.json")

# 支持的图片格式
SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')