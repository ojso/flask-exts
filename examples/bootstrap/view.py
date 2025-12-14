from flask import request, flash, redirect, url_for
from markupsafe import Markup
from flask_exts.admin import expose_url
from flask_exts.admin import View
from .forms import (
    HelloForm,
    TelephoneForm,
    ContactForm,
    IMForm,
    ButtonForm,
    ExampleForm,
    BootswatchForm,
)
from .models import Message
from flask_exts.datastore.sqla import db


class BootstrapView(View):
    @expose_url("/")
    def index(self):
        return self.render("bootstrap/index.html")

    @expose_url("/form", methods=["GET", "POST"])
    def test_form(self):
        form = HelloForm()
        if form.validate_on_submit():
            flash("Form validated!")
            return redirect(url_for(".index"))

        return self.render(
            "bootstrap/form.html",
            form=form,
            telephone_form=TelephoneForm(),
            contact_form=ContactForm(),
            im_form=IMForm(),
            button_form=ButtonForm(),
            example_form=ExampleForm(),
        )

    @expose_url("/nav", methods=["GET", "POST"])
    def test_nav(self):
        return self.render("bootstrap/nav.html")

    @expose_url("/bootswatch", methods=["GET", "POST"])
    def test_bootswatch(self):
        form = BootswatchForm()
        if form.validate_on_submit():
            flash(f"Render style has been set to {form.theme_name.data}.")
        return self.render("bootstrap/bootswatch.html", form=form)

    @expose_url("/pagination", methods=["GET", "POST"])
    def test_pagination(self):
        page = request.args.get("page", 1, type=int)
        pagination = Message.query.paginate(page=page, per_page=10)
        messages = pagination.items
        return self.render(
            "bootstrap/pagination.html", pagination=pagination, messages=messages
        )

    @expose_url("/flash", methods=["GET", "POST"])
    def test_flash(self):
        flash("A simple default alert—check it out!")
        flash("A simple primary alert—check it out!", "primary")
        flash("A simple secondary alert—check it out!", "secondary")
        flash("A simple success alert—check it out!", "success")
        flash("A simple danger alert—check it out!", "danger")
        flash("A simple warning alert—check it out!", "warning")
        flash("A simple info alert—check it out!", "info")
        flash("A simple light alert—check it out!", "light")
        flash("A simple dark alert—check it out!", "dark")
        flash(
            Markup(
                'A simple success alert with <a href="#" class="alert-link">an example link</a>. Give it a click if you like.'
            ),
            "success",
        )
        return self.render("bootstrap/flash.html")

    @expose_url("/table")
    def test_table(self):
        page = request.args.get("page", 1, type=int)
        pagination = Message.query.paginate(page=page, per_page=10)
        messages = pagination.items
        titles = [
            ("id", "#"),
            ("text", "Message"),
            ("author", "Author"),
            ("category", "Category"),
            ("draft", "Draft"),
            ("create_time", "Create Time"),
        ]
        data = []
        for msg in messages:
            data.append(
                {
                    "id": msg.id,
                    "text": msg.text,
                    "author": msg.author,
                    "category": msg.category,
                    "draft": msg.draft,
                    "create_time": msg.create_time,
                }
            )
        return self.render(
            "bootstrap/table.html",
            messages=messages,
            titles=titles,
            Message=Message,
            data=data,
        )

    @expose_url("/table/<int:message_id>/view")
    def view_message(self, message_id):
        message = Message.query.get(message_id)
        if message:
            return f'Viewing {message_id} with text "{message.text}". Return to <a href="/table">table</a>.'
        return f'Could not view message {message_id} as it does not exist. Return to <a href="/table">table</a>.'

    @expose_url("/table/<int:message_id>/edit")
    def edit_message(self, message_id):
        message = Message.query.get(message_id)
        if message:
            message.draft = not message.draft
            db.session.commit()
            return f'Message {message_id} has been editted by toggling draft status. Return to <a href="/table">table</a>.'
        return f'Message {message_id} did not exist and could therefore not be edited. Return to <a href="/table">table</a>.'

    @expose_url("/table/<int:message_id>/delete", methods=["POST"])
    def delete_message(self, message_id):
        message = Message.query.get(message_id)
        if message:
            db.session.delete(message)
            db.session.commit()
            return f'Message {message_id} has been deleted. Return to <a href="/table">table</a>.'
        return f'Message {message_id} did not exist and could therefore not be deleted. Return to <a href="/table">table</a>.'

    @expose_url("/table/<int:message_id>/like")
    def like_message(self, message_id):
        return f'Liked the message {message_id}. Return to <a href="/table">table</a>.'

    @expose_url("/table/new-message")
    def new_message(self):
        return 'Here is the new message page. Return to <a href="/table">table</a>.'

    @expose_url("/icon")
    def test_icon(self):
        return self.render("bootstrap/icon.html")

    @expose_url("/icons")
    def test_icons(self):
        return self.render("bootstrap/icons.html")
