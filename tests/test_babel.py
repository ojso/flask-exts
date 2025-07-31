import pytest
from datetime import datetime
from flask import session
from flask_babel import get_locale
from flask_babel import get_timezone
from flask_babel import format_datetime
from flask_babel import refresh
from flask_babel import gettext
from flask_babel import get_translations
from wtforms.fields import StringField
from wtforms.validators import DataRequired
from flask_exts.template.form.flask_form import FlaskForm
from flask_exts.template.fields import JSONField


def test_locale(app):
    with app.test_request_context():
        locale = get_locale()
        timezone = get_timezone()
        # print("locale:",get_locale().language)
        # print("timezone:",get_timezone().zone)
        # print(format_datetime(datetime.now(), "full"))
        # print(format_datetime(datetime.now()))
        assert "China Standard Time" in format_datetime(datetime.now(), "full")
        assert get_locale().language == "en"
        assert get_timezone().zone == app.config.get("BABEL_DEFAULT_TIMEZONE")
        assert get_timezone().zone == "Asia/Shanghai"
        # 修改语言为zh
        session["lang"] = "zh"
        # print("locale:",get_locale().language)
        assert get_locale().language == "en"
        refresh()
        # print("locale:",get_locale().language)
        assert get_locale().language == "zh"
        # print(format_datetime(datetime.now(), "full"))
        assert "中国标准时间" in format_datetime(datetime.now(), "full")
        # print(format_datetime(datetime.now()))


def test_translation(app):
    text = "Name"
    text_en = "Name"
    text_zh = "名称"
    with app.test_request_context():
        assert gettext(text) == text_en
        session["lang"] = "zh"
        refresh()
        assert gettext(text) == text_zh


def test_translation_form(app):
    text_required = "This field is required."
    text_required_en = "This field is required."
    text_required_zh = "此字段是必需项."
    text_invalid_json = "Invalid JSON"
    text_invalid_json_en = "Invalid JSON"
    text_invalid_json_zh = "无效的JSON"

    class F(FlaskForm):
        name = StringField(validators=[DataRequired()])
        json = JSONField()

    with app.test_request_context(method="POST", data={"json": "abc"}):
        session["lang"] = "en"
        # print(gettext("Invalid JSON"))
        f = F()
        f.validate()
        # print(f.name.errors)
        # print(f.json.errors)
        # print(f.name())
        # print(f.json())
        assert text_required_en in f.name.errors
        assert text_invalid_json_en in f.json.errors

        session["lang"] = "zh"
        refresh()
        f = F()
        f.validate()
        # print(f.name.errors)
        # print(f.json.errors)
        assert text_required_zh in f.name.errors
        assert text_invalid_json_zh in f.json.errors

@pytest.mark.skip(reason="skip.")
def test_babel_get_translations(app):
    with app.test_request_context():
        session["lang"] = "zh"
        t = get_translations()
        # print(t._catalog)
        for k, v in t._catalog.items():
            print(f"{k} -> {v}")

@pytest.mark.skip(reason="skip.")
def test_GNUTranslations(app):
    from gettext import GNUTranslations
    import os.path

    messages_mo = os.path.join(
        app.root_path, "translations", "zh_CN", "LC_MESSAGES", "messages.mo"
    )
    print(messages_mo)
    with open(messages_mo, "rb") as f:
        g = GNUTranslations(f)
    print(g._catalog)
    for k, v in g._catalog.items():
        print(k, v)
