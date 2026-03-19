"""
飞书配置
"""

# 飞书应用配置
FEISHU_APP_ID = "cli_a9f6f82a4ff89bd9"
FEISHU_APP_SECRET = "XSGDLKj0CAPvFYJPnDQMhexOdWcxS0ON"

# 目标用户
TARGET_USER_ID = "ou_0cdbe8a5a456c32beb95d46bb00b2bc1"  # 王波

# 多维表格配置
BITABLE_CONFIG = {
    "name": "AI论文预研助手 - 论文库",
    "description": "自动存储检索到的论文数据",
    "fields": [
        {"field_name": "论文标题", "field_type": 1},  # 文本
        {"field_name": "作者", "field_type": 1},  # 文本
        {"field_name": "发表时间", "field_type": 5},  # 日期
        {"field_name": "研究方法", "field_type": 1},  # 文本
        {"field_name": "数据集", "field_type": 1},  # 文本
        {"field_name": "核心结论", "field_type": 1},  # 文本
        {"field_name": "PDF链接", "field_type": 15},  # URL
        {"field_name": "研究课题", "field_type": 1},  # 文本
        {"field_name": "检索时间", "field_type": 5},  # 日期
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
    "time": "08:00",  # 每天8点推送
    "keywords": ["LLM", "Transformer", "AI", "机器学习"],  # 关注的关键词
    "max_papers": 10,  # 每天最多推送10篇
}

# 消息卡片配置
CARD_CONFIG = {
    "header_color": "blue",
    "show_actions": True,
    "actions": ["查看报告", "查看知识图谱", "查看对比矩阵"]
}
