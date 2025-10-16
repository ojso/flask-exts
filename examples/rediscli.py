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
redis_view = RedisCli(Redis())
manager.admin.add_view(redis_view)

if __name__ == "__main__":
    app.run(debug=True)
