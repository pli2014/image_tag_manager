import os
import dash
import dash_bootstrap_components as dbc
from flask import Flask, send_from_directory, abort
from config import IMAGE_DIRECTORIES
from layout import create_layout
from callbacks import register_callbacks
from urllib.parse import unquote
import logging
import json
from config import CACHE_FILE

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_cache_data():
    """
    加载缓存数据
    
    Returns:
        dict: 缓存数据
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def serve_image(filename):
    """
    为多个图片目录提供静态资源服务
    
    Args:
        filename (str): 请求的文件名（MD5文件名或相对路径）
        
    Returns:
        文件响应或404错误
    """
    try:
        # URL解码文件名
        decoded_filename = unquote(filename)
        logger.info(f"收到静态资源请求: filename={decoded_filename}")
        
        # 方法1: 通过读取缓存文件将MD5文件名转换为真实路径
        cache_data = load_cache_data()
        for real_path, data in cache_data.items():
            md5_path = data.get("md5_path", "")
            if md5_path == decoded_filename:
                # 验证文件是否存在
                if os.path.exists(real_path) and os.path.isfile(real_path):
                    # 找到匹配的MD5映射，使用真实路径提供文件
                    directory = os.path.dirname(real_path)
                    basename = os.path.basename(real_path)
                    logger.info(f"通过MD5映射找到资源: md5_path={decoded_filename}, real_path={real_path}")
                    return send_from_directory(directory, basename)
                else:
                    logger.warning(f"MD5映射找到但文件不存在: md5_path={decoded_filename}, real_path={real_path}")

        
        # 如果在所有地方都找不到文件，返回404
        logger.warning(f"静态资源未找到: filename={decoded_filename}, 搜索目录={IMAGE_DIRECTORIES}")
        abort(404)
    except Exception as e:
        logger.error(f"静态资源服务异常: {str(e)}")
        abort(500)


def create_app():
    """
    创建Dash应用实例
    
    Returns:
        dash.Dash: Dash应用实例
    """
    # 使用Flask服务器以便自定义路由
    server = Flask(__name__)
    
    # 注册图片服务路由
    server.add_url_rule('/assets/<path:filename>', 'serve_image', serve_image)
    
    # 初始化Dash应用
    app = dash.Dash(__name__, 
                   server=server,
                   external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = "图片标签管理器"
    
    # 设置应用布局
    app.layout = create_layout()
    
    # 注册回调函数
    register_callbacks(app)
    
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8050)