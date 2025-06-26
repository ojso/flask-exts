from ..utils.hasher import Blake2bHasher
from ..utils.serializer import TimedUrlSerializer


class Security:
    def __init__(
        self,
        app=None,
    ):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(
        self,
        app,
    ):
        self.app = app

        # hasher
        self.hasher = Blake2bHasher(app.config.get("SECRET_KEY"))
        # serializer
        self.serializer = TimedUrlSerializer(app.config.get("SECRET_KEY"))
