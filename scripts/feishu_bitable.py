#!/usr/bin/env python3
"""
飞书多维表格API调用示例
参考: https://open.feishu.cn/document/quick-access-to-base/step-2-download-and-run-sample-code
"""
import requests
import json
import time

# 飞书应用配置
APP_ID = "cli_a9f6f82a4ff89bd9"
APP_SECRET = "XSGDLKj0CAPvFYJPnDQMhexOdWcxS0ON"

# API基础URL
BASE_URL = "https://open.feishu.cn"

def get_tenant_access_token():
    """获取tenant_access_token"""
    url = f"{BASE_URL}/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        print(f"获取token失败: {result}")
        return None

def create_bitables_app(token, name):
    """创建多维表格应用"""
    url = f"{BASE_URL}/open-apis/bitable/v1/apps"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "name": name,
        "folder_token": ""  # 如果需要指定文件夹可以填写
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    print(f"创建多维表格响应: {result}")
    return result

def create_table(token, app_token, table_name):
    """在多维表格中创建表"""
    url = f"{BASE_URL}/open-apis/bitable/v1/apps/{app_token}/tables"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "table": {
            "name": table_name,
            "default_view_name": "默认视图",
            "fields": [
                {"field_name": "论文标题", "field_type": "Text"},
                {"field_name": "作者", "field_type": "Text"},
                {"field_name": "发表时间", "field_type": "DateTime"},
                {"field_name": "研究方法", "field_type": "SingleSelect", "options": ["Transformer", "BERT", "GPT", "其他"]},
                {"field_name": "数据集", "field_type": "MultiSelect", "options": ["ImageNet", "COCO", "WMT", "GLUE"]},
                {"field_name": "arXiv ID", "field_type": "Text"},
                {"field_name": "PDF链接", "field_type": "URL"}
            ]
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    print(f"创建表响应: {result}")
    return result

def insert_records(token, app_token, table_id, records):
    """插入记录"""
    url = f"{BASE_URL}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "records": records
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    print(f"插入记录响应: {result}")
    return result

def main():
    print("=" * 50)
    print("飞书多维表格API测试")
    print("=" * 50)
    
    # 1. 获取token
    print("\n[1] 获取tenant_access_token...")
    token = get_tenant_access_token()
    if not token:
        print("获取token失败，程序退出")
        return
    
    print(f"获取token成功: {token[:20]}...")
    
    # 2. 创建多维表格应用
    print("\n[2] 创建多维表格应用...")
    app_name = f"AI论文研究_{int(time.time())}"
    app_result = create_bitables_app(token, app_name)
    
    if app_result.get("code") != 0:
        print(f"创建多维表格失败: {app_result}")
        return
    
    app_token = app_result["data"]["app"]["app_token"]
    print(f"创建成功! app_token: {app_token}")
    
    # 3. 创建表
    print("\n[3] 创建数据表...")
    table_result = create_table(token, app_token, "论文数据")
    
    if table_result.get("code") != 0:
        print(f"创建表失败: {table_result}")
        return
    
    table_id = table_result["data"]["table"]["table_id"]
    print(f"创建成功! table_id: {table_id}")
    
    # 4. 插入数据
    print("\n[4] 插入论文数据...")
    records = [
        {
            "fields": {
                "论文标题": "Attention Is All You Need",
                "作者": "Vaswani et al.",
                "研究方法": "Transformer",
                "arXiv ID": "1706.03762",
                "PDF链接": "https://arxiv.org/pdf/1706.03762"
            }
        },
        {
            "fields": {
                "论文标题": "BERT: Pre-training of Deep Bidirectional Transformers",
                "作者": "Devlin et al.",
                "研究方法": "BERT",
                "arXiv ID": "1810.04805",
                "PDF链接": "https://arxiv.org/pdf/1810.04805"
            }
        },
        {
            "fields": {
                "论文标题": "Language Models are Few-Shot Learners",
                "作者": "Brown et al.",
                "研究方法": "GPT",
                "arXiv ID": "2005.14165",
                "PDF链接": "https://arxiv.org/pdf/2005.14165"
            }
        }
    ]
    
    insert_result = insert_records(token, app_token, table_id, records)
    
    if insert_result.get("code") != 0:
        print(f"插入数据失败: {insert_result}")
        return
    
    print(f"插入成功! 共插入 {len(records)} 条记录")
    
    # 5. 输出结果
    print("\n" + "=" * 50)
    print("🎉 成功创建多维表格!")
    print("=" * 50)
    print(f"\n多维表格App Token: {app_token}")
    print(f"表格ID: {table_id}")
    print(f"\n访问链接: https://my.feishu.cn/base/{app_token}")
    print("\n请复制上述链接到浏览器中访问")

if __name__ == "__main__":
    main()
