from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 模拟数据
items = [
    {"id": 1, "name": "项目A", "price": 99.9, "active": True,  "created": "2025-01-15 10:30:00"},
    {"id": 2, "name": "项目B", "price": 199,  "active": False, "created": "2025-03-20 14:00:00"},
    {"id": 3, "name": "项目C", "price": 59.5, "active": True,  "created": "2025-06-01 09:15:00"},
]

# 字段类型定义（告诉前端用什么控件编辑）
FIELD_TYPES = {
    "name":    {"type": "text",     "label": "名称"},
    "price":   {"type": "number",   "label": "价格"},
    "active":  {"type": "bool",     "label": "启用"},
    "created": {"type": "datetime", "label": "创建时间"},
}

@app.route("/")
def index():
    return render_template("index.html", items=items, field_types=FIELD_TYPES)

@app.route("/api/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    """AJAX 更新接口"""
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        return jsonify({"success": False, "error": "未找到"}), 404

    data = request.get_json()
    field = data.get("field")
    value = data.get("value")

    # 类型转换
    if field == "price":
        value = float(value)
    elif field == "active":
        value = value in (True, "true", "1", 1)
    elif field == "created":
        value = datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")

    item[field] = value
    return jsonify({"success": True, "field": field, "value": value, "display": str(value)})

if __name__ == "__main__":
    app.run(debug=True)