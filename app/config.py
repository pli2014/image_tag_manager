import os

# 图片目录配置 - 支持多个目录
# 可以通过逗号分隔指定多个目录，或者使用环境变量 IMAGE_DIRECTORIES
IMAGE_DIRECTORIES = os.getenv("IMAGE_DIRECTORIES", "")

# 阿里云百炼配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

# 缓存文件路径
CACHE_FILE = os.getenv("CACHE_FILE", "./cache.json")

# 支持的图片格式
SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')