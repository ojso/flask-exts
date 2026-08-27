"""
=============================================================
WTForms + Bootstrap 5：处理 FieldList 和 FormField
=============================================================
FieldList：字段列表（如多个邮箱）
FormField：嵌套表单（如地址信息）
FieldList + FormField：表单列表（如多个收货地址）
"""


# ============================================================
#  模拟数据结构
# ============================================================
print("=" * 60)
print("三种场景")
print("=" * 60)

print("""
场景 1：FieldList —— 多个同类型字段
  用户有多个邮箱：[email1, email2, email3]

场景 2：FormField —— 嵌套表单
  用户有地址信息：{省, 市, 街道}

场景 3：FieldList + FormField —— 表单列表
  用户有多个收货地址：[{省,市,街道}, {省,市,街道}, ...]
""")


# ============================================================
#  Jinja2 宏 —— 完整版（处理所有情况）
# ============================================================

BS5_FORM_MACROS = """
{# ============================================================ #}
{# Bootstrap 5 完整表单宏（支持 FieldList / FormField）         #}
{# ============================================================ #}

{# ---------------------------------------------------------- #}
{# render_field：渲染单个字段                                  #}
{# ---------------------------------------------------------- #}
{% macro render_field(field, label_class="form-label", wrapper_class="mb-3", **kwargs) %}
  {% if field.type == "BooleanField" %}
    <div class="{{ wrapper_class }} form-check">
      {{ field(class="form-check-input", **kwargs) }}
      <label class="form-check-label" for="{{ field.id }}">{{ field.label.text }}</label>
      {% for error in field.errors %}
        <div class="invalid-feedback">{{ error }}</div>
      {% endfor %}
    </div>

  {% elif field.type == "SelectField" %}
    <div class="{{ wrapper_class }}">
      <label class="{{ label_class }}" for="{{ field.id }}">{{ field.label.text }}</label>
      {{ field(class="form-select", **kwargs) }}
      {% for error in field.errors %}
        <div class="invalid-feedback">{{ error }}</div>
      {% endfor %}
    </div>

  {% elif field.type == "SubmitField" %}
    <div class="{{ wrapper_class }}">
      {{ field(class="btn btn-primary", **kwargs) }}
    </div>

  {% elif field.type == "HiddenField" %}
    {{ field() }}

  {% elif field.type == "FormField" %}
    {{ render_formfield(field) }}

  {% elif field.type == "FieldList" %}
    {{ render_fieldlist(field) }}

  {% else %}
    <div class="{{ wrapper_class }}">
      <label class="{{ label_class }}" for="{{ field.id }}">{{ field.label.text }}</label>
      {{ field(class="form-control", **kwargs) }}
      {% for error in field.errors %}
        <div class="invalid-feedback">{{ error }}</div>
      {% endfor %}
    </div>
  {% endif %}
{% endmacro %}


{# ---------------------------------------------------------- #}
{# render_formfield：嵌套表单（如地址信息）                     #}
{# 用 Bootstrap Card 包裹，视觉上区分层级                       #}
{# ---------------------------------------------------------- #}
{% macro render_formfield(formfield, card_class="card mb-3", body_class="card-body") %}
  <fieldset class="{{ card_class }}">
    <div class="{{ body_class }}">
      {% if formfield.label.text %}
        <legend class="fs-5 mb-3">{{ formfield.label.text }}</legend>
      {% endif %}

      {% for field in formfield %}
        {% if field.type not in ("CSRFTokenField", "HiddenField") %}
          {{ render_field(field) }}
        {% else %}
          {{ field() }}
        {% endif %}
      {% endfor %}
    </div>
  </fieldset>
{% endmacro %}


{# ---------------------------------------------------------- #}
{# render_fieldlist：字段列表                                  #}
{# 每个元素用 Card 包裹，带删除按钮                             #}
{# ---------------------------------------------------------- #}
{% macro render_fieldlist(fieldlist) %}
  <div class="mb-3" id="fieldlist-{{ fieldlist.id }}">
    {% if fieldlist.label.text %}
      <label class="form-label fw-bold">{{ fieldlist.label.text }}</label>
    {% endif %}

    {% for field in fieldlist %}
      <div class="card mb-2 fieldlist-item">
        <div class="card-body d-flex align-items-start gap-2">
          <div class="flex-grow-1">
            {% if field.type == "FormField" %}
              {# FieldList 里嵌套 FormField #}
              {% for subfield in field %}
                {% if subfield.type not in ("CSRFTokenField", "HiddenField") %}
                  {{ render_field(subfield) }}
                {% else %}
                  {{ subfield() }}
                {% endif %}
              {% endfor %}
            {% else %}
              {# 普通字段列表 #}
              {{ field(class="form-control") }}
              {% for error in field.errors %}
                <div class="invalid-feedback">{{ error }}</div>
              {% endfor %}
            {% endif %}
          </div>
          <button type="button" class="btn btn-outline-danger btn-sm"
                  onclick="this.closest('.fieldlist-item').remove()">
            ✕
          </button>
        </div>
      </div>
    {% endfor %}

    {# 添加按钮 #}
    <button type="button" class="btn btn-outline-secondary btn-sm"
            onclick="addFieldListItem('fieldlist-{{ fieldlist.id }}', '{{ fieldlist.id }}')">
      + 添加
    </button>

    {# 错误信息 #}
    {% for error in fieldlist.errors %}
      <div class="text-danger mt-1">{{ error }}</div>
    {% endfor %}
  </div>
{% endmacro %}


{# ---------------------------------------------------------- #}
{# render_form：渲染整个表单                                   #}
{# ---------------------------------------------------------- #}
{% macro render_form(form, layout="vertical") %}
  {% for field in form %}
    {{ render_field(field) }}
  {% endfor %}
{% endmacro %}
"""


# ============================================================
#  Python 端：模拟 render_fieldlist 的输出
# ============================================================
print("=" * 60)
print("【场景 1】FieldList —— 多个邮箱")
print("=" * 60)

print("""
Python 端：
  class UserForm(Form):
      emails = FieldList(StringField("邮箱"), min_entries=1)

模板端：
  {{ render_field(form.emails) }}

HTML 输出（Bootstrap 5）：
""")

# 模拟输出
html_fieldlist_simple = """
  <div class="mb-3" id="fieldlist-emails">
    <label class="form-label fw-bold">邮箱</label>

    <div class="card mb-2 fieldlist-item">
      <div class="card-body d-flex align-items-start gap-2">
        <div class="flex-grow-1">
          <input type="text" name="emails-0" class="form-control" value="alice@example.com">
        </div>
        <button type="button" class="btn btn-outline-danger btn-sm"
                onclick="this.closest('.fieldlist-item').remove()">✕</button>
      </div>
    </div>

    <div class="card mb-2 fieldlist-item">
      <div class="card-body d-flex align-items-start gap-2">
        <div class="flex-grow-1">
          <input type="text" name="emails-1" class="form-control" value="bob@example.com">
        </div>
        <button type="button" class="btn btn-outline-danger btn-sm"
                onclick="this.closest('.fieldlist-item').remove()">✕</button>
      </div>
    </div>

    <button type="button" class="btn btn-outline-secondary btn-sm"
            onclick="addFieldListItem('fieldlist-emails', 'emails')">+ 添加</button>
  </div>
"""
print(html_fieldlist_simple)


print("\n" + "=" * 60)
print("【场景 2】FormField —— 嵌套表单（地址信息）")
print("=" * 60)

print("""
Python 端：
  class AddressForm(Form):
      province = StringField("省")
      city     = StringField("市")
      street   = StringField("街道")

  class UserForm(Form):
      username = StringField("用户名")
      address  = FormField(AddressForm, "地址信息")

模板端：
  {{ render_field(form.address) }}

HTML 输出（Bootstrap 5，用 Card 包裹嵌套表单）：
""")

html_formfield = """
  <fieldset class="card mb-3">
    <div class="card-body">
      <legend class="fs-5 mb-3">地址信息</legend>

      <div class="mb-3">
        <label class="form-label" for="address-province">省</label>
        <input type="text" name="address-province" class="form-control" value="广东">
      </div>

      <div class="mb-3">
        <label class="form-label" for="address-city">市</label>
        <input type="text" name="address-city" class="form-control" value="深圳">
      </div>

      <div class="mb-3">
        <label class="form-label" for="address-street">街道</label>
        <input type="text" name="address-street" class="form-control" value="科技园路1号">
      </div>
    </div>
  </fieldset>
"""
print(html_formfield)


print("\n" + "=" * 60)
print("【场景 3】FieldList + FormField —— 多个地址")
print("=" * 60)

print("""
Python 端：
  class AddressForm(Form):
      province = StringField("省")
      city     = StringField("市")
      street   = StringField("街道")

  class UserForm(Form):
      username  = StringField("用户名")
      addresses = FieldList(FormField(AddressForm), min_entries=1)

模板端：
  {{ render_field(form.addresses) }}

HTML 输出（Card 列表，每个地址一个 Card）：
""")

html_fieldlist_formfield = """
  <div class="mb-3" id="fieldlist-addresses">
    <label class="form-label fw-bold">收货地址</label>

    <!-- 地址 1 -->
    <div class="card mb-2 fieldlist-item">
      <div class="card-body d-flex align-items-start gap-2">
        <div class="flex-grow-1">
          <div class="mb-3">
            <label class="form-label">省</label>
            <input type="text" name="addresses-0-province" class="form-control" value="广东">
          </div>
          <div class="mb-3">
            <label class="form-label">市</label>
            <input type="text" name="addresses-0-city" class="form-control" value="深圳">
          </div>
          <div class="mb-3">
            <label class="form-label">街道</label>
            <input type="text" name="addresses-0-street" class="form-control" value="科技园路1号">
          </div>
        </div>
        <button type="button" class="btn btn-outline-danger btn-sm"
                onclick="this.closest('.fieldlist-item').remove()">✕</button>
      </div>
    </div>

    <!-- 地址 2 -->
    <div class="card mb-2 fieldlist-item">
      <div class="card-body d-flex align-items-start gap-2">
        <div class="flex-grow-1">
          <div class="mb-3">
            <label class="form-label">省</label>
            <input type="text" name="addresses-1-province" class="form-control" value="北京">
          </div>
          <div class="mb-3">
            <label class="form-label">市</label>
            <input type="text" name="addresses-1-city" class="form-control" value="北京">
          </div>
          <div class="mb-3">
            <label class="form-label">街道</label>
            <input type="text" name="addresses-1-street" class="form-control" value="中关村大街1号">
          </div>
        </div>
        <button type="button" class="btn btn-outline-danger btn-sm"
                onclick="this.closest('.fieldlist-item').remove()">✕</button>
      </div>
    </div>

    <button type="button" class="btn btn-outline-secondary btn-sm"
            onclick="addFieldListItem('fieldlist-addresses', 'addresses')">+ 添加地址</button>
  </div>
"""
print(html_fieldlist_formfield)


# ============================================================
#  JavaScript：动态添加 FieldList 项目
# ============================================================
print("\n" + "=" * 60)
print("JavaScript：动态添加 FieldList 项目")
print("=" * 60)

js_code = """
<script>
function addFieldListItem(containerId, fieldName) {
    const container = document.getElementById(containerId);
    const items = container.querySelectorAll('.fieldlist-item');
    const newIndex = items.length;

    // 创建新卡片
    const card = document.createElement('div');
    card.className = 'card mb-2 fieldlist-item';

    // 判断是 FieldList<FormField> 还是 FieldList<普通字段>
    const firstItem = items[0];
    if (firstItem && firstItem.querySelector('[name*="-"]')) {
        // FormField 模式：复制结构，替换索引
        card.innerHTML = firstItem.innerHTML.replace(
            new RegExp(fieldName + '-\\\\d+', 'g'),
            fieldName + '-' + newIndex
        );
        // 清空值
        card.querySelectorAll('input, select, textarea').forEach(el => el.value = '');
    } else {
        // 普通字段模式
        card.innerHTML = `
            <div class="card-body d-flex align-items-start gap-2">
                <div class="flex-grow-1">
                    <input type="text" name="${fieldName}-${newIndex}" class="form-control">
                </div>
                <button type="button" class="btn btn-outline-danger btn-sm"
                        onclick="this.closest('.fieldlist-item').remove()">✕</button>
            </div>
        `;
    }

    // 插入到"添加"按钮之前
    container.insertBefore(card, container.querySelector('button'));
}
</script>
"""
print(js_code)


# ============================================================
#  完整宏文件（可直接使用）
# ============================================================
print("\n" + "=" * 60)
print("完整宏文件：bs5_form.html（可直接复制到项目）")
print("=" * 60)

complete_macros = '''
{# bs5_form.html — Bootstrap 5 WTForms 完整宏 #}

{# ========== 渲染单个字段 ========== #}
{% macro render_field(field, label_class="form-label", wrapper_class="mb-3", **kwargs) %}
  {%- if field.type == "BooleanField" -%}
    <div class="{{ wrapper_class }} form-check">
      {{ field(class="form-check-input", **kwargs) }}
      <label class="form-check-label" for="{{ field.id }}">{{ field.label.text }}</label>
      {%- for error in field.errors -%}
        <div class="invalid-feedback">{{ error }}</div>
      {%- endfor -%}
    </div>

  {%- elif field.type == "SelectField" -%}
    <div class="{{ wrapper_class }}">
      <label class="{{ label_class }}" for="{{ field.id }}">{{ field.label.text }}</label>
      {{ field(class="form-select", **kwargs) }}
      {%- for error in field.errors -%}
        <div class="invalid-feedback">{{ error }}</div>
      {%- endfor -%}
    </div>

  {%- elif field.type == "SubmitField" -%}
    <div class="{{ wrapper_class }}">
      {{ field(class="btn btn-primary", **kwargs) }}
    </div>

  {%- elif field.type == "HiddenField" -%}
    {{ field() }}

  {%- elif field.type == "FormField" -%}
    {{ _render_formfield(field) }}

  {%- elif field.type == "FieldList" -%}
    {{ _render_fieldlist(field) }}

  {%- else -%}
    <div class="{{ wrapper_class }}">
      <label class="{{ label_class }}" for="{{ field.id }}">{{ field.label.text }}</label>
      {{ field(class="form-control", **kwargs) }}
      {%- for error in field.errors -%}
        <div class="invalid-feedback">{{ error }}</div>
      {%- endfor -%}
    </div>
  {%- endif -%}
{% endmacro %}


{# ========== FormField（嵌套表单） ========== #}
{% macro _render_formfield(formfield) %}
  <fieldset class="card mb-3">
    <div class="card-body">
      {%- if formfield.label.text -%}
        <legend class="fs-5 mb-3">{{ formfield.label.text }}</legend>
      {%- endif -%}
      {%- for field in formfield -%}
        {%- if field.type == "HiddenField" -%}
          {{ field() }}
        {%- elif field.type != "CSRFTokenField" -%}
          {{ render_field(field) }}
        {%- endif -%}
      {%- endfor -%}
    </div>
  </fieldset>
{% endmacro %}


{# ========== FieldList（字段列表） ========== #}
{% macro _render_fieldlist(fieldlist) %}
  <div class="mb-3" id="fieldlist-{{ fieldlist.id }}">
    {%- if fieldlist.label.text -%}
      <label class="form-label fw-bold">{{ fieldlist.label.text }}</label>
    {%- endif -%}

    {%- for field in fieldlist -%}
      <div class="card mb-2 fieldlist-item">
        <div class="card-body d-flex align-items-start gap-2">
          <div class="flex-grow-1">
            {%- if field.type == "FormField" -%}
              {# FieldList<FormField> #}
              {%- for subfield in field -%}
                {%- if subfield.type == "HiddenField" -%}
                  {{ subfield() }}
                {%- elif subfield.type != "CSRFTokenField" -%}
                  {{ render_field(subfield) }}
                {%- endif -%}
              {%- endfor -%}
            {%- else -%}
              {# FieldList<普通字段> #}
              {{ field(class="form-control") }}
              {%- for error in field.errors -%}
                <div class="invalid-feedback">{{ error }}</div>
              {%- endfor -%}
            {%- endif -%}
          </div>
          <button type="button" class="btn btn-outline-danger btn-sm flex-shrink-0"
                  onclick="this.closest(\'.fieldlist-item\').remove()">✕</button>
        </div>
      </div>
    {%- endfor -%}

    <button type="button" class="btn btn-outline-secondary btn-sm"
            data-fieldlist="{{ fieldlist.id }}"
            onclick="bs5AddFieldList(this)">+ 添加</button>

    {%- for error in fieldlist.errors -%}
      <div class="text-danger mt-1">{{ error }}</div>
    {%- endfor -%}
  </div>
{% endmacro %}


{# ========== 渲染整个表单 ========== #}
{% macro render_form(form) %}
  {%- for field in form -%}
    {{ render_field(field) }}
  {%- endfor -%}
{% endmacro %}


{# ========== JavaScript（放在 </body> 前） ========== #}
{% macro bs5_fieldlist_js() %}
<script>
function bs5AddFieldList(btn) {
    const fieldName = btn.dataset.fieldlist.replace(\'fieldlist-\', \'\');
    const container = btn.closest(\'[id^="fieldlist-"]\');
    const items = container.querySelectorAll(\'.fieldlist-item\');
    const newIndex = items.length;
    const firstItem = items[0];
    const card = document.createElement(\'div\');
    card.className = \'card mb-2 fieldlist-item\';

    if (firstItem && firstItem.querySelector(\'[name*="-"]\')) {
        card.innerHTML = firstItem.innerHTML.replace(
            new RegExp(fieldName + \'-\\\\d+\', \'g\'), fieldName + \'-\' + newIndex
        );
        card.querySelectorAll(\'input,select,textarea\').forEach(el => el.value = \'\');
    } else {
        card.innerHTML = `
            <div class="card-body d-flex align-items-start gap-2">
                <div class="flex-grow-1">
                    <input type="text" name="${fieldName}-${newIndex}" class="form-control">
                </div>
                <button type="button" class="btn btn-outline-danger btn-sm flex-shrink-0"
                        onclick="this.closest(\'.fieldlist-item\').remove()">✕</button>
            </div>`;
    }
    container.insertBefore(card, btn);
}
</script>
{% endmacro %}
'''

print(complete_macros)


# ============================================================
#  使用示例
# ============================================================
print("\n" + "=" * 60)
print("使用示例")
print("=" * 60)

usage = """
Python 端（完全不用改）：

  class AddressForm(Form):
      province = StringField("省", validators=[DataRequired()])
      city     = StringField("市", validators=[DataRequired()])
      street   = StringField("街道")

  class UserForm(Form):
      username  = StringField("用户名", validators=[DataRequired()])
      emails    = FieldList(StringField("邮箱"), min_entries=1)
      address   = FormField(AddressForm, "默认地址")
      addresses = FieldList(FormField(AddressForm, "收货地址"), min_entries=1)
      submit    = SubmitField("提交")


模板端：

  {% from "bs5_form.html" import render_form, render_field, bs5_fieldlist_js %}

  <form method="POST">
    {{ form.hidden_tag() }}

    {# 普通字段 #}
    {{ render_field(form.username) }}

    {# 字段列表（多个邮箱） #}
    {{ render_field(form.emails) }}

    {# 嵌套表单（地址） #}
    {{ render_field(form.address) }}

    {# 字段列表 + 嵌套表单（多个地址） #}
    {{ render_field(form.addresses) }}

    {# 提交按钮 #}
    {{ render_field(form.submit) }}
  </form>

  {# 放在 </body> 前 #}
  {{ bs5_fieldlist_js() }}


关键：宏自动识别字段类型
  StringField       → <input class="form-control">
  SelectField       → <select class="form-select">
  BooleanField      → <input class="form-check-input">
  FormField         → <fieldset class="card"> 包裹
  FieldList         → Card 列表 + 添加/删除按钮
  FieldList+FormField → Card 列表，每个 Card 里是嵌套表单
"""
print(usage)


print("\n" + "=" * 60)
print("总结")
print("=" * 60)
print("""
FieldList / FormField 的 Bootstrap 5 渲染策略：

┌───────────────────┬──────────────────────────────────────┐
│ 字段类型           │ Bootstrap 5 渲染方式                  │
├───────────────────┼──────────────────────────────────────┤
│ FormField         │ <fieldset class="card"> 包裹          │
│                   │ 视觉上区分嵌套层级                      │
├───────────────────┼──────────────────────────────────────┤
│ FieldList         │ 每个元素一个 <div class="card">       │
│ (普通字段)         │ + ✕ 删除按钮 + 添加按钮              │
├───────────────────┼──────────────────────────────────────┤
│ FieldList         │ 每个元素一个 Card                     │
│ + FormField       │ Card 内部是嵌套的字段组                │
│                   │ + ✕ 删除按钮 + 添加按钮              │
├───────────────────┼──────────────────────────────────────┤
│ 动态添加           │ JavaScript：复制第一个 item            │
│                   │ 替换索引，清空值，插入 DOM             │
└───────────────────┴──────────────────────────────────────┘

核心思想：
  宏里判断 field.type，递归处理嵌套结构
  模板中只用 render_field()，不关心内部实现
""")
