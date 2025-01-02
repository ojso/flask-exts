import os.path as op
from flask import render_template
from flask_exts.forms.form import FlaskForm
from flask_exts.forms.fields import FileField,ImageField
from flask_exts.forms.validators import FileRequired


def register_blueprints(app):
    save_path = op.join(app.root_path, "tmp")
    class FileUploadForm(FlaskForm):
        upload = FileField(
            "Upload", save_path=save_path, validators=[FileRequired()]
        )
    
    class ImageUploadForm(FlaskForm):
        upload = ImageField(
            "Upload", save_path=save_path, validators=[FileRequired()]
        )

    @app.route("/")
    def hello():
        return render_template("hello.html")

    @app.route("/upload", methods=("GET", "POST"))
    def upload():
        form = FileUploadForm()
        if form.validate_on_submit():
            form.upload.save_file()
        return render_template("upload.html", form=form)
    
    @app.route("/upload2", methods=("GET", "POST"))
    def upload_image():
        form = ImageUploadForm()
        if form.validate_on_submit():
            form.upload.save_file()
        return render_template("upload.html", form=form)
