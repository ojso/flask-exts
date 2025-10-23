from flask import Flask
from flask_exts import Manager
from flask_exts.datastore.sqla import db
from flask_exts.views.rediscli.view import RedisCli

# from redis import Redis
from flask_exts.views.rediscli.mock_redis import MockRedis as Redis

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"

# Manager init
manager = Manager()
manager.init_app(app)

# add rediscli view
# redis_view = RedisCli(Redis())
redis_view = RedisCli(Redis())
manager.admin.add_view(redis_view)

with app.app_context():
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)