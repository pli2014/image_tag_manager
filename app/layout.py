import dash_bootstrap_components as dbc
from dash import html, dcc
from config import IMAGE_DIRECTORIES


def create_layout():
    """
    创建应用布局
    
    Returns:
        dbc.Container: 应用布局容器
    """
    return dbc.Container([
        # 页面标题
        dbc.Row([
            dbc.Col([
                html.H1("图片标签管理器", className="text-center", 
                       style={"fontWeight": "300", "margin": "20px 0", "color": "#333"})
            ])
        ]),
        
        # 主要内容区域
        dbc.Row([
            # 左侧控制面板
            dbc.Col([
                # 配置卡片
                dbc.Card([
                    dbc.CardBody([
                        html.H5("配置", className="card-title", 
                               style={"fontWeight": "500", "marginBottom": "15px"}),
                        dbc.InputGroup([
                            dbc.InputGroupText("图片目录", 
                                             style={"borderRadius": "8px 0 0 8px", "border": "1px solid #e0e0e0"}),
                            dbc.Input(id="image-directory", value=",".join(IMAGE_DIRECTORIES), type="text",
                                    style={"borderRadius": "0 8px 8px 0", "border": "1px solid #e0e0e0"})
                        ], className="mb-3"),
                        html.Small("支持多个目录，用逗号分隔", className="form-text text-muted mb-3"),
                        dbc.Button("全量扫描", id="full-scan", 
                                 style={"borderRadius": "8px", "marginRight": "10px", 
                                        "backgroundColor": "#007AFF", "border": "none"}),
                        dbc.Button("增量扫描", id="incremental-scan", 
                                 style={"borderRadius": "8px", "backgroundColor": "#34C759", "border": "none"}),
                        html.Div(id="scan-status", className="mt-3")
                    ])
                ], style={"borderRadius": "12px", "boxShadow": "0 2px 10px rgba(0,0,0,0.05)", "border": "none"}),
                
                # 统计信息卡片
                dbc.Card([
                    dbc.CardBody([
                        html.H5("统计信息", className="card-title", 
                               style={"fontWeight": "500", "marginBottom": "15px"}),
                        html.P(id="total-images", children="总图片数: 0", 
                              style={"marginBottom": "5px", "fontSize": "14px", "color": "#666"}),
                        html.P(id="processed-images", children="已处理图片数: 0", 
                              style={"marginBottom": "5px", "fontSize": "14px", "color": "#666"}),
                        html.P(id="total-tokens", children="总Token消耗: 0", 
                              style={"marginBottom": "0", "fontSize": "14px", "color": "#666"})
                    ])
                ], style={"borderRadius": "12px", "boxShadow": "0 2px 10px rgba(0,0,0,0.05)", "border": "none", 
                         "marginTop": "20px"})
            ], width=12, lg=4),
            
            # 右侧展示区域
            dbc.Col([
                # 标签过滤区域
                dbc.Card([
                    dbc.CardBody([
                        html.H5("标签过滤", className="card-title", 
                               style={"fontWeight": "500", "marginBottom": "15px"}),
                        html.Div(id="tag-tabs-container", 
                               style={"display": "flex", "flexWrap": "wrap", "gap": "8px"})
                    ])
                ], style={"borderRadius": "12px", "boxShadow": "0 2px 10px rgba(0,0,0,0.05)", "border": "none", 
                         "marginBottom": "20px"}),
                
                # 图片展示区域
                dbc.Card([
                    dbc.CardBody([
                        html.H5("图片展示", className="card-title", 
                               style={"fontWeight": "500", "marginBottom": "15px"}),
                        html.Div(id="image-gallery", children=[], 
                               style={
                                   "display": "flex",
                                   "flexWrap": "wrap",
                                   "justifyContent": "flex-start",
                                   "alignContent": "flex-start",
                                   "overflowY": "auto", 
                                   "maxHeight": "70vh", 
                                   "minHeight": "500px",
                                   "padding": "5px"
                               })
                    ])
                ], style={
                    "borderRadius": "12px", 
                    "boxShadow": "0 2px 10px rgba(0,0,0,0.05)", 
                    "border": "none"
                })
            ], width=12, lg=8)
        ]),
        
        # 存储缓存数据
        dcc.Store(id="cache-data", data={}),
        
        # 存储选中的标签
        dcc.Store(id="selected-tag-storage", storage_type="session")
        
    ], fluid=True, style={"padding": "20px", "backgroundColor": "#f5f5f7", "minHeight": "100vh"})