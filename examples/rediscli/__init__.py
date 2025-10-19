from redis import Redis
from flask import Flask
from flask_exts import Manager
from flask_exts.views.rediscli.view import RedisCli
from flask_exts.views.rediscli.mock_redis import MockRedis

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"

# Manager init
manager = Manager()
manager.init_app(app)

# add rediscli
# redis_view = RedisCli(Redis())
# for test without a real redis server, use MockRedis
redis_view = RedisCli(MockRedis())
manager.admin.add_view(redis_view)
