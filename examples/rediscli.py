from redis import Redis
from flask import Flask
from flask_exts import Manager
from flask_exts.views.rediscli_view import RedisCli

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
# Manager init
manager = Manager()
manager.init_app(app)
# add rediscli
admin = app.extensions["admin"][0]
redis_view = RedisCli(Redis())
admin.add_view(redis_view)

if __name__ == "__main__":
    app.run(debug=True)
