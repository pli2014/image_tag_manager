# 图片标签管理器

一个基于阿里云百炼Qwen-VL-Max模型的图片标签管理工具，支持图片自动打标、分类和展示。

## 功能特性

- 自动扫描图片目录，支持全量和增量扫描
- 使用阿里云百炼Qwen-VL-Max模型进行图片内容识别和打标
- 标签信息缓存到本地文件，避免重复处理
- Web界面展示图片和标签信息
- 统计显示处理图片数量和消耗的token数量

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 设置环境变量：
   - `DASHSCOPE_API_KEY`: 阿里云百炼API密钥
   - `IMAGE_DIRECTORY`: 图片目录路径（可选，默认为`./images`）
   - `CACHE_FILE`: 缓存文件路径（可选，默认为`./cache.json`）

2. 或者直接修改 `app/config.py` 文件中的配置项

## 使用方法

1. 将图片放入配置的图片目录中
2. 运行应用：
   ```bash
   python app/app.py
   ```
3. 在浏览器中打开 `http://localhost:8050` 访问应用界面
4. 点击"全量扫描"或"增量扫描"按钮开始处理图片

## 项目结构

```
image_tag_manager/
├── app/
│   ├── __init__.py
│   ├── app.py          # 主应用文件
│   ├── config.py       # 配置文件
│   └── image_processor.py  # 图片处理模块
├── images/             # 示例图片目录
├── cache.json          # 缓存文件
├── requirements.txt    # 依赖列表
└── README.md           # 说明文档
```