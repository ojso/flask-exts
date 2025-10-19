import pytest
from redis import Redis
from flask_exts.views.rediscli.view import RedisCli


class TestRedisCliView:
    def test_rediscli(self, client,admin):
        redis_view = RedisCli(Redis())
        admin.add_view(redis_view)

        rv = client.get("/admin/rediscli/")
        assert rv.status_code == 200
