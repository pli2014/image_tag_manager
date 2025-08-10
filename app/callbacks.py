import os
import re
from dash import ctx, callback_context, no_update
import dash
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from dash import html, dcc
from image_processor import process_images
from utils import get_cache_data, calculate_total_tokens, extract_tags, simplify_labels, get_image_url
from config import IMAGE_DIRECTORIES


def register_callbacks(app):
    """
    注册所有回调函数
    
    Args:
        app: Dash应用实例
    """
    
    # 更新统计信息
    @app.callback(
        [Output("total-images", "children"),
         Output("processed-images", "children"),
         Output("total-tokens", "children")],
        Input("cache-data", "data")
    )
    def update_statistics(cache_data):
        if not cache_data:
            cache_data = get_cache_data()
        
        total_images = len(cache_data)
        processed_images = len([v for v in cache_data.values() if v.get("labels")])
        total_tokens = calculate_total_tokens(cache_data)
        
        return (
            f"总图片数: {total_images}",
            f"已处理图片数: {processed_images}",
            f"总Token消耗: {total_tokens}"
        )

    # 更新标签tabs
    @app.callback(
        [Output("tag-tabs-container", "children"),
         Output("selected-tag-storage", "data", allow_duplicate=True)],
        [Input("cache-data", "data"),
         Input("selected-tag-storage", "data")],
        prevent_initial_call="initial_duplicate"
    )
    def update_tag_tabs(cache_data, stored_selected_tag):
        if not cache_data:
            cache_data = get_cache_data()
        
        tags = extract_tags(cache_data)
        # 添加"全部"选项
        tags = ["全部"] + tags
        
        if not tags:
            return html.P("暂无标签"), stored_selected_tag
        
        # 确定当前应该选中的标签，如果存储的标签不在当前标签列表中，则默认选择"全部"
        selected_tag = stored_selected_tag if stored_selected_tag in tags else "全部"
        
        # 创建tabs
        tabs = []
        for tag in tags:
            is_active = (tag == selected_tag)
            tab = dbc.Button(
                tag,
                id={"type": "tag-tab", "index": tag},
                className="me-2 mb-2",
                style={
                    "borderRadius": "20px",
                    "backgroundColor": "#007AFF" if is_active else "#ffffff",
                    "border": f"1px solid {'#007AFF' if is_active else '#e0e0e0'}",
                    "color": "#ffffff" if is_active else "#333",
                    "fontSize": "14px",
                    "padding": "6px 16px",
                    "boxShadow": "0 1px 2px rgba(0,0,0,0.05)",
                    "cursor": "pointer"
                },
                n_clicks=1 if is_active and tag != "全部" else 0  # 确保"全部"标签的n_clicks为0
            )
            tabs.append(tab)
        
        return html.Div(tabs, style={"display": "flex", "flexWrap": "wrap", "gap": "8px"}), selected_tag

    # 处理标签tab点击事件
    @app.callback(
        Output("selected-tag-storage", "data"),
        Input({"type": "tag-tab", "index": ALL}, "n_clicks"),
        State({"type": "tag-tab", "index": ALL}, "id"),
        prevent_initial_call=True
    )
    def update_selected_tag(n_clicks, ids):
        # 确定哪个标签被点击
        ctx = callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
            
        # 获取被点击的标签
        clicked_tag = None
        for trigger in ctx.triggered:
            if "tag-tab" in trigger['prop_id']:
                prop_id = trigger['prop_id'].split('.')[0]
                try:
                    import json
                    prop_dict = json.loads(prop_id)
                    clicked_tag = prop_dict.get("index")
                except:
                    pass
        
        if clicked_tag is not None:
            return clicked_tag
        else:
            raise dash.exceptions.PreventUpdate

    # 更新图片展示
    @app.callback(
        Output("image-gallery", "children"),
        [Input("cache-data", "data"),
         Input("selected-tag-storage", "data")],  # 监听标签按钮点击和存储的选中标签
        prevent_initial_call=False
    )
    def update_gallery(cache_data, selected_tag):
        if not cache_data:
            cache_data = get_cache_data()
        
        # 构建标签到图片的映射
        tag_to_images = {}
        for image_path, data in cache_data.items():
            if not data.get("labels"):
                continue
                
            # 处理标签，提取标签列表
            if isinstance(data["labels"], list):
                image_tags = data["labels"]
            else:
                # 确保data["labels"]是字符串
                labels_str = str(data["labels"])
                # 如果标签是字符串，尝试提取关键词作为标签
                image_tags = re.findall(r'[\u4e00-\u9fff]+', labels_str)
            
            # 如果没有提取到标签，则使用"未分类"作为标签
            if not image_tags:
                image_tags = ["未分类"]
            
            # 将图片添加到每个标签的列表中
            # 确保不会添加重复的图片到同一个标签下
            for tag in image_tags:
                if tag not in tag_to_images:
                    tag_to_images[tag] = []
                # 确保不会添加重复的图片到同一个标签下
                if not any(image[0] == image_path for image in tag_to_images[tag]):
                    tag_to_images[tag].append((image_path, data))
        
        # 如果有选中的标签，只展示该标签的图片
        if selected_tag and selected_tag != "全部":
            images_to_show = tag_to_images.get(selected_tag, [])
        else:
            # 默认展示所有图片，需要去重
            images_to_show = []
            seen_images = set()
            for images in tag_to_images.values():
                for image in images:
                    image_path = image[0]  # image是一个元组(image_path, data)
                    if image_path not in seen_images:
                        images_to_show.append(image)
                        seen_images.add(image_path)
        
        # 创建图片卡片
        cards = []
        for image_path, data in images_to_show:
            # 处理标签显示
            if isinstance(data["labels"], list):
                display_labels = " ".join(data["labels"])
            else:
                display_labels = str(data["labels"])
            
            # 获取图片URL，使用MD5路径映射
            image_url = get_image_url(image_path, cache_data)
            
            # 创建300*300的展示区块，优化图片展示效果
            card = dbc.Card([
                dbc.CardImg(src=image_url, 
                           top=True, 
                           style={
                               "width": "300px", 
                               "height": "300px", 
                               "objectFit": "cover",
                               "borderRadius": "8px 8px 0 0"
                           }),
                dbc.CardBody([
                    html.H6(os.path.basename(image_path), 
                           className="card-title", 
                           style={
                               "fontSize": "14px",
                               "fontWeight": "500",
                               "marginBottom": "5px",
                               "overflow": "hidden",
                               "textOverflow": "ellipsis",
                               "whiteSpace": "nowrap"
                           }),
                    html.P(display_labels, 
                          className="card-text",
                          style={
                              "fontSize": "12px",
                              "color": "#666",
                              "marginBottom": "5px",
                              "height": "40px",
                              "overflow": "hidden"
                          }),
                    html.Small(f"Tokens: {data.get('token_usage', {}).get('total_tokens', 0)}", 
                              className="text-muted",
                              style={"fontSize": "11px"})
                ], style={"padding": "10px"})
            ], className="mb-3", 
            style={
                "display": "inline-block", 
                "margin": "5px",
                "borderRadius": "8px",
                "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                "border": "none",
                "width": "300px",
                "verticalAlign": "top"
            })
            
            cards.append(card)
        
        if not cards:
            return html.P("没有找到匹配的图片。")
        
        # 使用div容器包装所有卡片，实现5列平铺效果
        return html.Div(cards, style={"display": "flex", "flexWrap": "wrap"})
        
    # 处理扫描按钮点击
    @app.callback(
        [Output("scan-status", "children"),
         Output("cache-data", "data")],
        [Input("full-scan", "n_clicks"),
         Input("incremental-scan", "n_clicks")],
        State("image-directory", "value")
    )
    def handle_scan(full_clicks, incremental_clicks, directory_value):
        # 确定触发回调的按钮
        triggered_id = ctx.triggered_id
        
        if triggered_id is None:
            return "", get_cache_data()
        
        # 解析目录输入（支持多个目录，用逗号分隔）
        directories = []
        if directory_value:
            directories = [d.strip() for d in directory_value.split(",") if d.strip()]
        
        # 如果没有提供目录，则使用默认配置
        if not directories:
            directories = IMAGE_DIRECTORIES
        
        # 执行扫描
        try:
            if triggered_id == "full-scan":
                result = process_images(directories, incremental=False)
                message = f"全量扫描完成，处理了 {result['processed_count']} 张图片，消耗 {result['total_tokens']} tokens"
            else:
                result = process_images(directories, incremental=True)
                message = f"增量扫描完成，处理了 {result['processed_count']} 张图片，消耗 {result['total_tokens']} tokens"
            
            # 返回成功消息和更新后的缓存数据
            return message, result["cache"]
        except Exception as e:
            # 返回错误消息
            return f"扫描出错: {str(e)}", get_cache_data()

    # 定期更新缓存数据
    @app.callback(
        Output("cache-data", "data", allow_duplicate=True),
        Input("interval-component", "n_intervals"),
        prevent_initial_call=True
    )
    def update_cache_data(n):
        return get_cache_data()