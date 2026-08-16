from flask_login import LoginManager
from ..security.auth_crypt import authorization_decoder
from ..proxies import _userstore


def user_loader(user_id):
    return _userstore.user_loader(int(user_id))


def load_user_from_request(request):
    # first, try to login using the api_key url arg
    # api_key = request.args.get('api_key')
    # if api_key:
    #     user = User.query.filter_by(api_key=api_key).first()
    #     if user:
    #         return user

    # next, try to login using Basic Auth
    # Basic is vulnerable, and not to use.
    # api_key = request.headers.get('Authorization')
    # if api_key:
    #     api_key = api_key.replace('Basic ', '', 1)
    #     try:
    #         api_key = base64.b64decode(api_key)
    #     except TypeError:
    #         pass
    #     user = User.query.filter_by(api_key=api_key).first()
    #     if user:
    #         return user

    # next, try to login using Bearer Jwt and load user

    if "Authorization" in request.headers:
        authstr = request.headers.get("Authorization")
        payload = authorization_decoder(authstr)
        if isinstance(payload, dict):
            if "id" in payload and payload["id"] is not None:
                user = _userstore.get_user_by_id(int(payload["id"]))
                if user:
                    return user
            identity = payload.get(_userstore.identity_name)
            if identity is not None:
                user = _userstore.get_user_by_identity(identity)
                if user:
                    return user
    # add other methods to get user

    # finally, return None if both methods did not login the user
    return None


def init_login(app):
    if not hasattr(app, "login_manager"):
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = "user.login"
        # login_manager.login_message = "Please login in"
        login_manager.user_loader(user_loader)
        login_manager.request_loader(load_user_from_request)
