"""
飞书配置 - 复制为 feishu_config.py 并填入你的真实值
"""

# 飞书应用配置（从飞书开放平台获取）
FEISHU_APP_ID = "your_app_id"
FEISHU_APP_SECRET = "your_app_secret"

# 目标用户 open_id（接收消息、多维表格链接推送的用户）
TARGET_USER_ID = "your_open_id"

# 多维表格配置
BITABLE_CONFIG = {
    "name": "AI论文预研助手 - 论文库",
    "description": "自动存储检索到的论文数据",
    "fields": [
        {"field_name": "论文标题", "field_type": 1},
        {"field_name": "作者", "field_type": 1},
        {"field_name": "发表时间", "field_type": 5},
        {"field_name": "研究方法", "field_type": 1},
        {"field_name": "数据集", "field_type": 1},
        {"field_name": "核心结论", "field_type": 1},
        {"field_name": "PDF链接", "field_type": 15},
        {"field_name": "研究课题", "field_type": 1},
        {"field_name": "检索时间", "field_type": 5},
    ]
}

# 知识库配置
WIKI_CONFIG = {
    "space_name": "AI论文预研知识库",
    "description": "自动归档研究报告和可视化内容"
}

# 每日推送配置
DAILY_PUSH_CONFIG = {
    "enabled": True,
    "time": "08:00",
    "keywords": ["LLM", "Transformer", "AI", "机器学习"],
    "max_papers": 10,
}

# 消息卡片配置
CARD_CONFIG = {
    "header_color": "blue",
    "show_actions": True,
    "actions": ["查看报告", "查看知识图谱", "查看对比矩阵"]
}
