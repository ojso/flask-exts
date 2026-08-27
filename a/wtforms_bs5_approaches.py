"""
=============================================================
WTForms + Bootstrap 5：两种实现方式对比
=============================================================
方式A：改写所有 Field/Widget（Python 端解决）
方式B：模板中 render_field() 函数（模板端解决）
"""


# ============================================================
#  方式 A：改写所有 Field —— Python 端解决
# ============================================================
print("=" * 60)
print("方式 A：自定义 Widget + Field")
print("=" * 60)

"""
需要为每种字段都写一个 Widget 和一个 Field：

  BS5StringField      → BS5TextInput
  BS5PasswordField    → BS5PasswordInput
  BS5EmailField       → BS5EmailInput
  BS5IntegerField     → BS5NumberInput
  BS5FloatField       → BS5NumberInput
  BS5DecimalField     → BS5NumberInput
  BS5TextAreaField    → BS5TextArea
  BS5SelectField      → BS5Select
  BS5RadioField       → BS5RadioInput
  BS5BooleanField     → BS5CheckboxInput
  BS5FileField        → BS5FileInput
  BS5DateField        → BS5DateInput
  BS5DateTimeField    → BS5DateTimeInput
  ...

代码量：约 200-300 行
维护成本：高（WTForms 升级可能要跟着改）
"""

from wtforms import Form, StringField, PasswordField, BooleanField, SelectField, TextAreaField, IntegerField, validators


# --- 自定义 Widget ---
class BS5TextInput:
    def __call__(self, field, **kwargs):
        kwargs["class"] = "form-control"
        if field.errors:
            kwargs["class"] += " is-invalid"
        kwargs.setdefault("id", field.id)
        return f'<input type="text" name="{field.name}" value="{field.data or ""}" {_dict_to_attrs(kwargs)}>'


class BS5PasswordInput:
    def __call__(self, field, **kwargs):
        kwargs["class"] = "form-control"
        if field.errors:
            kwargs["class"] += " is-invalid"
        kwargs.setdefault("id", field.id)
        return f'<input type="password" name="{field.name}" {_dict_to_attrs(kwargs)}>'


class BS5SelectWidget:
    def __call__(self, field, **kwargs):
        kwargs["class"] = "form-select"  # 注意：select 用 form-select 不是 form-control
        if field.errors:
            kwargs["class"] += " is-invalid"
        options = "".join(
            f'<option value="{v}" {"selected" if v == field.data else ""}>{t}</option>'
            for v, t in field.choices
        )
        return f'<select name="{field.name}" {_dict_to_attrs(kwargs)}>{options}</select>'


class BS5CheckboxWidget:
    def __call__(self, field, **kwargs):
        kwargs["class"] = "form-check-input"  # checkbox 用不同的 class
        checked = "checked" if field.data else ""
        return f'<input type="checkbox" name="{field.name}" {checked} {_dict_to_attrs(kwargs)}>'


class BS5TextAreaWidget:
    def __call__(self, field, **kwargs):
        kwargs["class"] = "form-control"
        return f'<textarea name="{field.name}" {_dict_to_attrs(kwargs)}>{field.data or ""}</textarea>'


# --- 自定义 Field ---
class BS5StringField(StringField):
    widget = BS5TextInput()

class BS5PasswordField(PasswordField):
    widget = BS5PasswordInput()

class BS5SelectField(SelectField):
    widget = BS5SelectWidget()

class BS5BooleanField(BooleanField):
    widget = BS5CheckboxWidget()

class BS5TextAreaField(TextAreaField):
    widget = BS5TextAreaWidget()

class BS5IntegerField(IntegerField):
    widget = BS5TextInput()  # 简化


# --- 使用 ---
class UserForm_A(Form):
    """每个字段都要用 BS5 版本"""
    username = BS5StringField("用户名", validators=[validators.DataRequired()])
    password = BS5PasswordField("密码")
    role     = BS5SelectField("角色", choices=[("user", "用户"), ("admin", "管理员")])
    bio      = BS5TextAreaField("简介")
    agree    = BS5BooleanField("同意")


print("\n  表单定义（每个字段都要换成 BS5 版）：")
print("  class UserForm_A(Form):")
print("      username = BS5StringField(...)    ← 必须用 BS5 版")
print("      password = BS5PasswordField(...)  ← 必须用 BS5 版")
print("      role     = BS5SelectField(...)    ← 必须用 BS5 版")

form_a = UserForm_A(data={"username": "alice", "role": "user", "bio": "hello"})
print(f"\n  form_a.username() = {form_a.username()}")
print(f"  form_a.role()     = {form_a.role()}")
print(f"  form_a.agree()    = {form_a.agree()}")

print("""
  优点：
    ✅ 表单定义干净，渲染时无需关心样式
    ✅ 逻辑集中在 Python 端

  缺点：
    ❌ 要为每个字段类型写 Widget + Field（约 15+ 个类）
    ❌ 模板中无法灵活调整样式（比如某个字段想加 form-control-lg）
    ❌ label、errors、wrapper div 还要另外处理
    ❌ WTForms 升级时可能要跟着改 Widget
""")


# ============================================================
#  方式 B：模板中 render_field() 函数
# ============================================================
print("=" * 60)
print("方式 B：模板中 render_field() 函数")
print("=" * 60)

"""
不需要改任何 WTForms 的 Field/Widget！
在模板中（Jinja2）用一个函数处理所有 Bootstrap 5 样式。

Python 端保持原样：
  class UserForm(Form):
      username = StringField(...)     ← 用原生 Field
      password = PasswordField(...)   ← 用原生 Field

模板端统一处理样式。
"""

# --- Jinja2 宏（macros/bs5_form.html）---

BS5_MACROS = """
{# ============================================ #}
{# Bootstrap 5 表单宏                           #}
{# ============================================ #}

{# 渲染单个字段 #}
{% macro render_field(field, label_class="form-label", wrapper_class="mb-3", **kwargs) %}
  {% if field.type == "BooleanField" %}
    <div class="{{ wrapper_class }} form-check">
      {{ field(class="form-check-input", **kwargs) }}
      <label class="form-check-label" for="{{ field.id }}">{{ field.label.text }}</label>
      {% for error in field.errors %}
        <div class="invalid-feedback">{{ error }}</div>
      {% endfor %}
    </div>
  {% else %}
    <div class="{{ wrapper_class }}">
      <label class="{{ label_class }}" for="{{ field.id }}">{{ field.label.text }}</label>
      {% if field.type == "SelectField" %}
        {{ field(class="form-select", **kwargs) }}
      {% else %}
        {{ field(class="form-control", **kwargs) }}
      {% endif %}
      {% for error in field.errors %}
        <div class="invalid-feedback">{{ error }}</div>
      {% endfor %}
    </div>
  {% endif %}
{% endmacro %}

{# 渲染整个表单 #}
{% macro render_form(form, layout="vertical") %}
  {% if layout == "horizontal" %}
    {% for field in form %}
      {% if field.type == "SubmitField" %}
        <div class="mb-3 row">
          <div class="col-sm-3"></div>
          <div class="col-sm-9">{{ field(class="btn btn-primary") }}</div>
        </div>
      {% elif field.type == "BooleanField" %}
        <div class="mb-3 row">
          <div class="col-sm-3"></div>
          <div class="col-sm-9">
            <div class="form-check">
              {{ field(class="form-check-input") }}
              <label class="form-check-label">{{ field.label.text }}</label>
            </div>
          </div>
        </div>
      {% else %}
        <div class="mb-3 row">
          <label class="col-form-label col-sm-3">{{ field.label.text }}</label>
          <div class="col-sm-9">
            {% if field.type == "SelectField" %}
              {{ field(class="form-select") }}
            {% else %}
              {{ field(class="form-control") }}
            {% endif %}
            {% for error in field.errors %}
              <div class="invalid-feedback">{{ error }}</div>
            {% endfor %}
          </div>
        </div>
      {% endif %}
    {% endfor %}
  {% else %}
    {% for field in form %}
      {{ render_field(field) }}
    {% endfor %}
  {% endif %}
{% endmacro %}
"""


# --- 模拟 render_field 在 Python 中的效果 ---

def render_field(field, label_class="form-label", wrapper_class="mb-3", **kwargs):
    """
    模板中 render_field() 的 Python 模拟版。
    实际项目中用 Jinja2 宏实现。
    """
    is_invalid = " is-invalid" if field.errors else ""
    html = []

    # Checkbox 特殊处理
    if field.type == "BooleanField":
        checked = "checked" if field.data else ""
        html.append(f'<div class="{wrapper_class} form-check">')
        html.append(f'  <input type="checkbox" name="{field.name}" class="form-check-input{is_invalid}" {checked}>')
        html.append(f'  <label class="form-check-label" for="{field.id}">{field.label.text}</label>')
    # Select 特殊处理
    elif field.type == "SelectField":
        html.append(f'<div class="{wrapper_class}">')
        html.append(f'  <label class="{label_class}" for="{field.id}">{field.label.text}</label>')
        options = "".join(
            f'<option value="{v}" {"selected" if v == field.data else ""}>{t}</option>'
            for v, t in field.choices
        )
        html.append(f'  <select name="{field.name}" class="form-select{is_invalid}" id="{field.id}">{options}</select>')
    # Submit 特殊处理
    elif field.type == "SubmitField":
        html.append(f'<div class="{wrapper_class}">')
        html.append(f'  <button type="submit" class="btn btn-primary">{field.label.text}</button>')
    # 普通字段
    else:
        html.append(f'<div class="{wrapper_class}">')
        html.append(f'  <label class="{label_class}" for="{field.id}">{field.label.text}</label>')
        value = field.data or ""
        html.append(f'  <input type="text" name="{field.name}" value="{value}" class="form-control{is_invalid}" id="{field.id}" {_dict_to_attrs(kwargs)}>')

    # 错误信息
    if field.errors:
        for error in field.errors:
            html.append(f'  <div class="invalid-feedback">{error}</div>')

    html.append('</div>')
    return "\n".join(html)


# --- 使用原生 Field ---
class UserForm_B(Form):
    """用原生 WTForms Field，不改任何东西"""
    username = StringField("用户名", validators=[validators.DataRequired()])
    password = PasswordField("密码")
    role     = SelectField("角色", choices=[("user", "用户"), ("admin", "管理员")])
    bio      = TextAreaField("简介")
    agree    = BooleanField("同意")


print("\n  表单定义（用原生 Field，不改任何代码）：")
print("  class UserForm_B(Form):")
print("      username = StringField(...)       ← 用原生！")
print("      password = PasswordField(...)     ← 用原生！")
print("      role     = SelectField(...)       ← 用原生！")

form_b = UserForm_B(data={"username": "alice", "role": "user", "bio": "hello"})

print("\n  模板中使用：")
print('  {{ render_field(form.username) }}')
print('  {{ render_field(form.password, placeholder="至少6位") }}')
print('  {{ render_field(form.role) }}')

print("\n  渲染结果：")
for field in form_b:
    if field.type not in ("CSRFTokenField",):
        print(f"\n  {render_field(field)}")

# 演示额外 kwargs 传递
print("\n\n  传递额外参数：")
print('  {{ render_field(form.username, placeholder="请输入用户名", maxlength="20") }}')
print(f"  → {render_field(form_b.username, placeholder='请输入用户名', maxlength='20')}")

print("""
  优点：
    ✅ 零改动：Python 端用原生 Field，完全不改
    ✅ 一个宏搞定所有字段类型
    ✅ 模板中灵活控制：{{ render_field(field, placeholder="...") }}
    ✅ 样式和逻辑分离：前端改 Bootstrap 版本只改宏文件
    ✅ WTForms 升级不影响

  缺点：
    ❌ 模板中多了一层调用
    ❌ 需要写 Jinja2 宏（但只写一次）
""")


# ============================================================
#  对比总结
# ============================================================
print("=" * 60)
print("最终对比")
print("=" * 60)
print("""
┌─────────────────────────┬──────────────────────────┬──────────────────────────┐
│                         │ 方式A：改写 Field         │ 方式B：render_field()    │
├─────────────────────────┼──────────────────────────┼──────────────────────────┤
│ 代码量                  │ 200-300 行 Python        │ 50 行 Jinja2 宏          │
│ Python 端改动           │ 每个字段都要换 BS5 版     │ 零改动，用原生 Field      │
│ 模板端改动              │ 无                        │ 引入宏文件               │
│ 样式灵活性              │ 低（写死在 Widget 里）     │ 高（模板中随时加 kwargs） │
│ 维护成本                │ 高（WTForms 升级要跟进）   │ 低（宏独立于 WTForms）    │
│ 新增字段类型            │ 要写新的 Widget+Field     │ 宏里加一个 if/elif        │
│ 团队协作                │ 前后端都要懂 Python        │ 前端改宏，后端不动        │
│ 推荐度                  │ ⭐⭐                      │ ⭐⭐⭐⭐⭐                │
└─────────────────────────┴──────────────────────────┴──────────────────────────┘

结论：强烈推荐方式 B（render_field 宏）

实际项目做法：
  1. 写一个 bs5_form.html 宏文件（只写一次）
  2. 模板中 import 这个宏
  3. Python 端用原生 WTForms Field，不改任何东西
  4. 需要定制时：{{ render_field(field, class="form-control-lg") }}

如果你用 Flask，直接用 Bootstrap-Flask 库：
  pip install Bootstrap-Flask
  它已经帮你写好了所有宏，开箱即用。
""")


def _dict_to_attrs(d):
    """辅助函数：dict → HTML 属性字符串"""
    parts = []
    for k, v in d.items():
        if k == "class_":
            k = "class"
        if v is True:
            parts.append(k)
        elif v is not False and v is not None:
            parts.append(f'{k}="{v}"')
    return " ".join(parts)
