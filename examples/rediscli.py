from flask import Flask
from flask_exts import Exts
from flask_exts.datastore.sqla import db
from flask_exts.views.rediscli.view import RedisCli

# from redis import Redis
from flask_exts.views.rediscli.mock_redis import MockRedis as Redis

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"

# Exts init
exts = Exts()
exts.init_app(app)

# add rediscli view
# redis_view = RedisCli(Redis())
redis_view = RedisCli(Redis())
exts.admin.add_view(redis_view)

with app.app_context():
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)