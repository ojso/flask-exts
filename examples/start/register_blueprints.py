def register_blueprints(app):

    @app.route("/")
    def hello():
        return "Hello, World!"

    # from .demo import bp as demo_bp
    # app.register_blueprint(demo_bp)
