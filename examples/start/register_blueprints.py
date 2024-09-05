from flask import render_template
from flask_exts.forms.form.base_form import BaseForm
def register_blueprints(app):

    @app.route("/")
    def hello():
        return render_template("demo.html")
        return "Hello, World!"

    # from .demo import bp as demo_bp
    # app.register_blueprint(demo_bp)

    @app.route("/upload", methods=("GET", "POST"))
    def upload():
        class FileUploadForm(BaseForm):
            pass

        form = FileUploadForm()

        for _ in range(5):
            form.uploads.append_entry()

        filedata = []

        if form.validate_on_submit():
            for upload in form.uploads.entries:
                filedata.append(upload)

        return render_template("upload.html", form=form, filedata=filedata)