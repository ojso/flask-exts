"""
=============================================================
可编辑列表 —— 点击单元格弹出编辑表单，AJAX 提交
=============================================================
完整实现：HTML + CSS + JavaScript + Flask 后端
"""

# ============================================================
#  后端 Flask 代码
# ============================================================
print("=" * 60)
print("后端代码（Flask）")
print("=" * 60)

flask_backend = '''
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
'''
print(flask_backend)


# ============================================================
#  前端 HTML + CSS + JavaScript
# ============================================================
print("\n" + "=" * 60)
print("前端代码（HTML + CSS + JavaScript）")
print("=" * 60)

frontend_html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>可编辑列表</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        /* 可编辑单元格样式 */
        .editable-cell {
            cursor: pointer;
            position: relative;
            border-bottom: 1px dashed #0d6efd;
            transition: background 0.2s;
        }
        .editable-cell:hover {
            background: #e8f0fe;
        }
        .editable-cell::after {
            content: "✎";
            margin-left: 4px;
            color: #0d6efd;
            font-size: 0.8em;
        }

        /* 编辑中的状态 */
        .editing {
            background: #fff3cd !important;
        }
    </style>
</head>
<body class="p-4">

<div class="container">
    <h3>可编辑列表</h3>
    <p class="text-muted">点击带有 <span class="text-primary">✎</span> 标记的单元格进行编辑</p>

    <table class="table table-bordered table-hover">
        <thead class="table-light">
            <tr>
                <th>ID</th>
                <th>名称 <small class="text-danger">*</small></th>
                <th>价格 <small class="text-danger">*</small></th>
                <th>启用</th>
                <th>创建时间</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr data-item-id="{{ item.id }}">
                <td>{{ item.id }}</td>
                <td class="editable-cell" data-field="name" data-type="text">{{ item.name }}</td>
                <td class="editable-cell" data-field="price" data-type="number">{{ item.price }}</td>
                <td class="editable-cell" data-field="active" data-type="bool">
                    {% if item.active %}✅ 是{% else %}❌ 否{% endif %}
                </td>
                <td class="editable-cell" data-field="created" data-type="datetime">{{ item.created }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<!-- 编辑弹窗（Bootstrap Modal） -->
<div class="modal fade" id="editModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">编辑</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="editForm">
                    <div class="mb-3">
                        <label class="form-label" id="editLabel"></label>
                        <div id="editInputContainer"></div>
                        <div class="invalid-feedback" id="editError"></div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                <button type="button" class="btn btn-primary" id="editSaveBtn" onclick="saveEdit()">保存</button>
            </div>
        </div>
    </div>
</div>

<!-- Toast 提示 -->
<div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div id="resultToast" class="toast" role="alert">
        <div class="toast-header">
            <strong class="me-auto" id="toastTitle">提示</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body" id="toastBody"></div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
// ============================================================
//  全局变量
// ============================================================
let currentCell = null;    // 当前编辑的单元格
let currentField = null;   // 当前字段名
let currentType = null;    // 当前字段类型
let currentItemId = null;  // 当前行 ID
let editModal = null;

document.addEventListener("DOMContentLoaded", function() {
    editModal = new bootstrap.Modal(document.getElementById("editModal"));

    // 给所有可编辑单元格绑定点击事件
    document.querySelectorAll(".editable-cell").forEach(cell => {
        cell.addEventListener("click", function() {
            openEditModal(this);
        });
    });
});

// ============================================================
//  打开编辑弹窗
// ============================================================
function openEditModal(cell) {
    currentCell = cell;
    currentField = cell.dataset.field;
    currentType = cell.dataset.type;
    currentItemId = cell.closest("tr").dataset.itemId;

    // 设置标题
    document.getElementById("editLabel").textContent = cell.dataset.field;

    // 根据类型生成不同的输入控件
    const container = document.getElementById("editInputContainer");
    const currentValue = cell.textContent.trim();
    container.innerHTML = createInput(currentType, currentField, currentValue);

    // 清空错误
    document.getElementById("editError").style.display = "none";

    // 打开弹窗
    editModal.show();

    // 聚焦输入框
    const input = container.querySelector("input, select, textarea");
    if (input) setTimeout(() => input.focus(), 300);
}

// ============================================================
//  根据类型创建输入控件
// ============================================================
function createInput(type, field, value) {
    switch (type) {
        case "text":
            return `<input type="text" class="form-control" id="editValue" value="${escapeHtml(value)}">`;

        case "number":
            return `<input type="number" class="form-control" id="editValue" value="${value}" step="0.01">`;

        case "bool":
            const checked = (value.includes("是") || value === "true") ? "checked" : "";
            return `
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="editValue" ${checked}>
                    <label class="form-check-label" for="editValue">启用</label>
                </div>`;

        case "datetime":
            // 转换格式：2025-01-15 10:30:00 → 2025-01-15T10:30
            const dtValue = value.replace(" ", "T").substring(0, 16);
            return `<input type="datetime-local" class="form-control" id="editValue" value="${dtValue}">`;

        case "date":
            return `<input type="date" class="form-control" id="editValue" value="${value}">`;

        case "select":
            // 可扩展：从 data-options 获取选项
            return `<select class="form-select" id="editValue">
                        <option value="A">选项A</option>
                        <option value="B">选项B</option>
                    </select>`;

        default:
            return `<input type="text" class="form-control" id="editValue" value="${escapeHtml(value)}">`;
    }
}

// ============================================================
//  保存编辑
// ============================================================
function saveEdit() {
    const input = document.getElementById("editValue");
    let value;

    // 取值（根据类型）
    if (currentType === "bool") {
        value = input.checked;
    } else if (currentType === "number") {
        value = parseFloat(input.value);
        if (isNaN(value)) {
            showError("请输入有效数字");
            return;
        }
    } else {
        value = input.value.trim();
        if (!value) {
            showError("不能为空");
            return;
        }
    }

    // 禁用按钮，显示 loading
    const btn = document.getElementById("editSaveBtn");
    btn.disabled = true;
    btn.innerHTML = \'<span class="spinner-border spinner-border-sm"></span> 保存中...\';

    // AJAX 提交
    fetch(`/api/items/${currentItemId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            field: currentField,
            value: value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新单元格显示
            updateCellDisplay(currentCell, currentType, data);
            editModal.hide();
            showToast("success", "保存成功");
        } else {
            showError(data.error || "保存失败");
        }
    })
    .catch(err => {
        showError("网络错误：" + err.message);
    })
    .finally(() => {
        btn.disabled = false;
        btn.textContent = "保存";
    });
}

// ============================================================
//  更新单元格显示
// ============================================================
function updateCellDisplay(cell, type, data) {
    switch (type) {
        case "bool":
            cell.textContent = data.value ? "✅ 是" : "❌ 否";
            break;
        case "datetime":
        case "date":
            cell.textContent = data.display;
            break;
        default:
            cell.textContent = data.display;
    }

    // 高亮闪烁效果
    cell.classList.add("editing");
    setTimeout(() => cell.classList.remove("editing"), 1500);
}

// ============================================================
//  工具函数
// ============================================================
function showError(msg) {
    const el = document.getElementById("editError");
    el.textContent = msg;
    el.style.display = "block";
}

function showToast(type, message) {
    const toast = document.getElementById("resultToast");
    const title = document.getElementById("toastTitle");
    const body = document.getElementById("toastBody");

    title.textContent = type === "success" ? "✅ 成功" : "❌ 错误";
    body.textContent = message;
    toast.className = `toast show border-${type === "success" ? "success" : "danger"}`;
    new bootstrap.Toast(toast).show();
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// ============================================================
//  键盘快捷键：Enter 保存，Escape 取消
// ============================================================
document.addEventListener("keydown", function(e) {
    if (!editModal || !editModal._isShown) return;

    if (e.key === "Enter" && e.target.tagName !== "TEXTAREA") {
        e.preventDefault();
        saveEdit();
    } else if (e.key === "Escape") {
        editModal.hide();
    }
});
</script>

</body>
</html>
'''

print(frontend_html)


# ============================================================
#  写文件
# ============================================================
import os

output_dir = "/sessions/lucid-optimistic-dirac/mnt/outputs"

# 写 HTML
html_path = os.path.join(output_dir, "editable_list.html")
with open(html_path, "w", encoding="utf-8") as f:
    # 去掉 Python 的转义
    content = frontend_html.replace("\\'", "'").replace('\\"', '"')
    f.write(content)

# 写 Flask 后端
flask_path = os.path.join(output_dir, "editable_list_app.py")
with open(flask_path, "w", encoding="utf-8") as f:
    f.write(flask_backend.strip())


# ============================================================
#  总结
# ============================================================
print("\n" + "=" * 60)
print("总结：实现要点")
print("=" * 60)
print("""
┌─────────────────────┬──────────────────────────────────────────────┐
│ 要点                 │ 实现方式                                      │
├─────────────────────┼──────────────────────────────────────────────┤
│ 可点击的单元格        │ class="editable-cell" + cursor:pointer        │
│                     │ data-field="字段名" data-type="类型"          │
├─────────────────────┼──────────────────────────────────────────────┤
│ 弹窗编辑             │ Bootstrap Modal，根据 data-type 生成不同控件   │
│                     │ text → input[text]                            │
│                     │ number → input[number]                        │
│                     │ bool → checkbox (switch)                      │
│                     │ datetime → input[datetime-local]              │
├─────────────────────┼──────────────────────────────────────────────┤
│ AJAX 提交            │ fetch("/api/items/<id>", method: "PATCH")     │
│                     │ body: { field: "name", value: "新值" }        │
├─────────────────────┼──────────────────────────────────────────────┤
│ 成功后更新页面        │ 直接修改 cell.textContent                     │
│                     │ + 高亮闪烁效果                                │
├─────────────────────┼──────────────────────────────────────────────┤
│ 键盘快捷键           │ Enter → 保存，Escape → 取消                   │
├─────────────────────┼──────────────────────────────────────────────┤
│ 错误处理             │ 前端校验 + 后端返回错误 → 显示在弹窗里          │
└─────────────────────┴──────────────────────────────────────────────┘

数据流：
  点击单元格 → openEditModal()
            → 根据 data-type 生成输入控件
            → 用户修改 → 点击保存
            → fetch PATCH /api/items/<id>
            → 成功 → updateCellDisplay() 更新页面
                   + Toast 提示
                   + 高亮闪烁

扩展方向：
  ✅ 批量编辑（checkbox 选多行）
  ✅ 撤销功能（保存前记录旧值）
  ✅ 乐观更新（先改页面，失败再回滚）
  ✅ WebSocket 实时同步（多人编辑）
""")

print(f"\n文件已生成：")
print(f"  HTML: {html_path}")
print(f"  Flask: {flask_path}")
print(f"\n运行方式：")
print(f"  1. 把 HTML 放到 templates/ 目录")
print(f"  2. python editable_list_app.py")
print(f"  3. 打开 http://localhost:5000")
