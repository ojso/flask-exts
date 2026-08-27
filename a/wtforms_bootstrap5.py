"""
=============================================================
WTForms 扩展适配 Bootstrap 5
=============================================================
三种方式：
  1. 自定义 Widget（最底层、最灵活）
  2. 自定义 Field + Widget（推荐）
  3. 使用现成库 Bootstrap-Flask（最省事）
"""

# ============================================================
#  方式 1：自定义 Widget —— 最底层
#  Widget 负责把 Field 渲染成 HTML
# ============================================================

from wtforms import (
    StringField, PasswordField, EmailField, TextAreaField,
    SelectField, BooleanField, IntegerField, DateField,
    FileField, SubmitField, Form, validators
)
from wtforms.widgets import Input, TextArea, Select, CheckboxInput, FileInput


# ---------- Bootstrap 5 基础 Widget 混入 ----------

class BS5WidgetMixin:
    """Bootstrap 5 样式混入"""
    bs5_class = "form-control"

    def bs5_kwargs(self, kwargs):
        """注入 Bootstrap 5 的 class"""
        existing = kwargs.get("class", "") or kwargs.get("class_", "")
        if self.bs5_class and self.bs5_class not in existing:
            kwargs["class_"] = f"{self.bs5_class} {existing}".strip()
        return kwargs


class BS5TextInput(BS5WidgetMixin, Input):
    input_type = "text"

    def __call__(self, field, **kwargs):
        kwargs = self.bs5_kwargs(kwargs)
        return super().__call__(field, **kwargs)


class BS5PasswordInput(BS5WidgetMixin, Input):
    input_type = "password"

    def __call__(self, field, **kwargs):
        kwargs = self.bs5_kwargs(kwargs)
        return super().__call__(field, **kwargs)


class BS5EmailInput(BS5WidgetMixin, Input):
    input_type = "email"

    def __call__(self, field, **kwargs):
        kwargs = self.bs5_kwargs(kwargs)
        return super().__call__(field, **kwargs)


class BS5NumberInput(BS5WidgetMixin, Input):
    input_type = "number"

    def __call__(self, field, **kwargs):
        kwargs = self.bs5_kwargs(kwargs)
        return super().__call__(field, **kwargs)


class BS5TextArea(BS5WidgetMixin, TextArea):
    bs5_class = "form-control"

    def __call__(self, field, **kwargs):
        kwargs = self.bs5_kwargs(kwargs)
        return super().__call__(field, **kwargs)


class BS5Select(BS5WidgetMixin, Select):
    bs5_class = "form-select"  # Bootstrap 5 的 select 用 form-select

    def __call__(self, field, **kwargs):
        kwargs = self.bs5_kwargs(kwargs)
        return super().__call__(field, **kwargs)


class BS5CheckboxInput(BS5WidgetMixin, CheckboxInput):
    bs5_class = "form-check-input"

    def __call__(self, field, **kwargs):
        kwargs = self.bs5_kwargs(kwargs)
        return super().__call__(field, **kwargs)


class BS5FileInput(BS5WidgetMixin, FileInput):
    bs5_class = "form-control"

    def __call__(self, field, **kwargs):
        kwargs = self.bs5_kwargs(kwargs)
        return super().__call__(field, **kwargs)


# ---------- 自定义 Bootstrap 5 Field ----------

class BS5StringField(StringField):
    widget = BS5TextInput()


class BS5PasswordField(PasswordField):
    widget = BS5PasswordInput()


class BS5EmailField(EmailField):
    widget = BS5EmailInput()


class BS5TextAreaField(TextAreaField):
    widget = BS5TextArea()


class BS5SelectField(SelectField):
    widget = BS5Select()


class BS5BooleanField(BooleanField):
    widget = BS5CheckboxInput()


class BS5IntegerField(IntegerField):
    widget = BS5NumberInput()


class BS5FileField(FileField):
    widget = BS5FileInput()


# ---------- 使用示例 ----------

class UserForm_BS5Widget(Form):
    username = BS5StringField("用户名", validators=[validators.DataRequired()])
    password = BS5PasswordField("密码", validators=[validators.DataRequired(), validators.Length(min=6)])
    email = BS5EmailField("邮箱", validators=[validators.DataRequired(), validators.Email()])
    bio = BS5TextAreaField("简介")
    role = BS5SelectField("角色", choices=[("user", "普通用户"), ("admin", "管理员")])
    agree = BS5BooleanField("同意条款")
    avatar = BS5FileField("头像")
    submit = SubmitField("提交", render_kw={"class": "btn btn-primary"})


# ============================================================
#  方式 2：渲染完整字段（label + input + errors）
#  提供 render_bs5() 方法，一次渲染完整的 Bootstrap 5 字段组
# ============================================================

class BS5FieldMixin:
    """
    让字段自带 render_bs5() 方法，
    一次渲染 label + widget + errors，完整 Bootstrap 5 结构。
    """

    def render_bs5(self, label_class="form-label", wrapper_class="mb-3"):
        """渲染为完整的 Bootstrap 5 字段组"""
        html = []

        # 处理 checkbox 特殊布局
        is_checkbox = isinstance(self, BooleanField)

        if is_checkbox:
            html.append(f'<div class="{wrapper_class} form-check">')
            html.append(str(self()))
            html.append(f'  <label class="form-check-label" for="{self.id}">{self.label.text}</label>')
        else:
            html.append(f'<div class="{wrapper_class}">')
            html.append(f'  <label class="{label_class}" for="{self.id}">{self.label.text}</label>')
            html.append(str(self()))

        # 错误信息
        if self.errors:
            for error in self.errors:
                html.append(f'  <div class="invalid-feedback" style="display:block">{error}</div>')

        # help text
        if hasattr(self, 'description') and self.description:
            html.append(f'  <div class="form-text">{self.description}</div>')

        html.append('</div>')
        return "\n".join(html)


# 把 Mixin 注入到所有 BS5 字段
class BS5StringField2(BS5FieldMixin, BS5StringField):
    pass


class BS5PasswordField2(BS5FieldMixin, BS5PasswordField):
    pass


class BS5EmailField2(BS5FieldMixin, BS5EmailField):
    pass


class BS5TextAreaField2(BS5FieldMixin, BS5TextAreaField):
    pass


class BS5SelectField2(BS5FieldMixin, BS5SelectField):
    pass


class BS5BooleanField2(BS5FieldMixin, BS5BooleanField):
    pass


class BS5IntegerField2(BS5FieldMixin, BS5IntegerField):
    pass


class BS5FileField2(BS5FieldMixin, BS5FileField):
    pass


class UserForm_BS5Field(BS5FieldMixin, Form):
    """完整示例表单"""
    username = BS5StringField2("用户名", validators=[validators.DataRequired()])
    password = BS5PasswordField2("密码", validators=[validators.DataRequired(), validators.Length(min=6)])
    email = BS5EmailField2("邮箱", validators=[validators.DataRequired(), validators.Email()])
    age = BS5IntegerField2("年龄", description="请输入 18-120 之间的数字")
    bio = BS5TextAreaField2("简介")
    role = BS5SelectField2("角色", choices=[("user", "普通用户"), ("admin", "管理员")])
    agree = BS5BooleanField2("同意条款")
    avatar = BS5FileField2("头像")
    submit = SubmitField("提交", render_kw={"class": "btn btn-primary"})


# ============================================================
#  方式 3：Form 级别渲染 —— form.render_bs5()
#  一个方法渲染整个表单
# ============================================================

class BS5FormMixin:
    """
    Form 级别的 Bootstrap 5 渲染。
    支持：普通布局、水平布局、行内布局。
    """

    def render_bs5(self, layout="vertical"):
        """
        渲染整个表单。
        layout: "vertical" | "horizontal" | "inline"
        """
        if layout == "horizontal":
            return self._render_horizontal()
        elif layout == "inline":
            return self._render_inline()
        else:
            return self._render_vertical()

    def _render_vertical(self):
        html = []
        for field in self:
            if isinstance(field, SubmitField):
                html.append(f'<div class="mb-3">{field(class_="btn btn-primary")}</div>')
            elif isinstance(field, BooleanField):
                html.append(self._render_check_field(field))
            else:
                html.append(self._render_normal_field(field))
        return "\n".join(html)

    def _render_horizontal(self, label_cols="col-sm-3", input_cols="col-sm-9"):
        html = []
        for field in self:
            if isinstance(field, SubmitField):
                html.append(f'''
    <div class="mb-3 row">
      <div class="{label_cols}"></div>
      <div class="{input_cols}">
        {field(class_="btn btn-primary")}
      </div>
    </div>''')
            elif isinstance(field, BooleanField):
                html.append(self._render_check_field(field, horizontal=True, label_cols=label_cols, input_cols=input_cols))
            else:
                html.append(self._render_normal_field(field, horizontal=True, label_cols=label_cols, input_cols=input_cols))
        return "\n".join(html)

    def _render_inline(self):
        html = ['<div class="row g-3 align-items-end">']
        for field in self:
            if isinstance(field, SubmitField):
                html.append(f'  <div class="col-auto">{field(class_="btn btn-primary")}</div>')
            else:
                html.append('  <div class="col-auto">')
                if not isinstance(field, BooleanField):
                    html.append(f'    <label class="form-label" for="{field.id}">{field.label.text}</label>')
                html.append(f'    {field()}')
                if field.errors:
                    for error in field.errors:
                        html.append(f'    <div class="invalid-feedback" style="display:block">{error}</div>')
                html.append('  </div>')
        html.append('</div>')
        return "\n".join(html)

    def _render_normal_field(self, field, horizontal=False, label_cols="col-sm-3", input_cols="col-sm-9"):
        is_invalid = " is-invalid" if field.errors else ""
        extra = f'class="{field(class_="")}" ' if not field.errors else ""

        if horizontal:
            return f'''
    <div class="mb-3 row">
      <label class="col-form-label {label_cols}" for="{field.id}">{field.label.text}</label>
      <div class="{input_cols}">
        {str(field)}
        {self._render_errors(field)}
      </div>
    </div>'''
        else:
            return f'''
    <div class="mb-3">
      <label class="form-label" for="{field.id}">{field.label.text}</label>
      {str(field)}
      {self._render_errors(field)}
    </div>'''

    def _render_check_field(self, field, horizontal=False, label_cols="col-sm-3", input_cols="col-sm-9"):
        if horizontal:
            return f'''
    <div class="mb-3 row">
      <div class="{label_cols}"></div>
      <div class="{input_cols}">
        <div class="form-check">
          {str(field)}
          <label class="form-check-label" for="{field.id}">{field.label.text}</label>
        </div>
      </div>
    </div>'''
        else:
            return f'''
    <div class="mb-3 form-check">
      {str(field)}
      <label class="form-check-label" for="{field.id}">{field.label.text}</label>
    </div>'''

    def _render_errors(self, field):
        if not field.errors:
            return ""
        return "\n".join(f'      <div class="invalid-feedback" style="display:block">{e}</div>' for e in field.errors)


class UserForm_BS5Form(BS5FormMixin, Form):
    """完整表单 —— 支持多种布局"""
    username = BS5StringField("用户名", validators=[validators.DataRequired()])
    password = BS5PasswordField("密码", validators=[validators.DataRequired(), validators.Length(min=6)])
    email = BS5EmailField("邮箱", validators=[validators.DataRequired(), validators.Email()])
    age = BS5IntegerField("年龄")
    bio = BS5TextAreaField("简介")
    role = BS5SelectField("角色", choices=[("user", "普通用户"), ("admin", "管理员")])
    agree = BS5BooleanField("同意条款")
    avatar = BS5FileField("头像")
    submit = SubmitField("提交")


# ============================================================
#  演示输出
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("方式1：自定义 Widget（只改 input 的 class）")
    print("=" * 60)

    form1 = UserForm_BS5Widget()
    print("\n  form1.username():")
    print(f"  {form1.username()}")
    print(f"\n  form1.role():")
    print(f"  {form1.role()}")
    print(f"\n  form1.agree():")
    print(f"  {form1.agree()}")

    print("\n\n" + "=" * 60)
    print("方式2：字段级 render_bs5()（label + input + errors）")
    print("=" * 60)

    form2 = UserForm_BS5Field()
    # 模拟验证错误
    form2.validate()
    print("\n  form2.username.render_bs5():")
    print(form2.username.render_bs5())
    print("\n  form2.agree.render_bs5():")
    print(form2.agree.render_bs5())

    print("\n\n" + "=" * 60)
    print("方式3：表单级 render_bs5() —— 垂直布局")
    print("=" * 60)

    form3 = UserForm_BS5Form()
    form3.validate()
    print(form3.render_bs5("vertical"))

    print("\n\n" + "=" * 60)
    print("方式3：表单级 render_bs5() —— 水平布局")
    print("=" * 60)

    print(form3.render_bs5("horizontal"))

    print("\n\n" + "=" * 60)
    print("方式3：表单级 render_bs5() —— 行内布局")
    print("=" * 60)

    print(form3.render_bs5("inline"))

    print("\n\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    print("""
┌──────────────────────────┬──────────────────────────┬──────────────────────────┐
│ 方式                      │ 优点                      │ 缺点                      │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ 1. 自定义 Widget          │ 最底层，完全控制 HTML      │ 需要手动处理 label/errors  │
│    (BS5TextInput)        │ 可复用                     │ 代码量大                   │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ 2. 自定义 Field + Mixin   │ 字段自带 render_bs5()     │ 每个字段都要调用一次       │
│    (BS5FieldMixin)       │ 灵活，粒度适中             │                          │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ 3. Form Mixin             │ 一行渲染整个表单           │ 定制单个字段不太方便       │
│    (BS5FormMixin)        │ 支持多种布局               │                          │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ 4. Bootstrap-Flask 库     │ 现成的，Jinja2 宏         │ 多一个依赖                 │
│    (pip install)         │ 开箱即用                   │ 定制需要学它的 API         │
└──────────────────────────┴──────────────────────────┴──────────────────────────┘

推荐组合：方式2 + 方式3
  - 字段级别：render_bs5() 单独渲染
  - 表单级别：form.render_bs5() 一键渲染
  - 需要定制时：覆盖单个字段的 widget

实际项目中更推荐使用 Bootstrap-Flask：
  pip install Bootstrap-Flask
  然后在模板里用 {{ form.username() }} 自动渲染 Bootstrap 5 样式
""")
