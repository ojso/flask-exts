import pytest
from datetime import datetime
from flask import session
from flask_babel import get_locale
from flask_babel import get_timezone
from flask_babel import format_datetime
from flask_babel import refresh
from flask_babel import gettext
from flask_exts.babel import gettext as admin_gettext


class TestBabel:
    def test_locale(self, app):
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

    def test_babel(self, app):
        with app.test_request_context():
            text = "Home"
            gettext("Home")
            text_en = "Main Page"
            text_zh = "主页"
            assert gettext(text) == text_en
            session["lang"] = "zh"
            refresh()
            assert gettext(text) == text_zh

    def test_admin_translation(self, app):
        with app.test_request_context():
            text = "Home"
            text_en = "Home"
            text_zh = "首页"
            assert admin_gettext(text) == text_en
            session["lang"] = "zh"
            refresh()
            assert admin_gettext(text) == text_zh

