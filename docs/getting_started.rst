Getting Started
===============

This guide walks you through building a complete Flask application with Flask-Exts,
including user authentication, an admin panel, and database-driven management features.

Prerequisites
-------------

- Python 3.10+
- Basic knowledge of Flask and SQLAlchemy

Installation
------------

.. code-block:: console

   pip install flask-exts

Quick Start
-----------

The simplest Flask-Exts application looks like this:

.. code-block:: python

   # app.py
   from flask import Flask
   from flask_exts import ExtensionManager
   from flask_exts.datastore.sqla import db

   app = Flask(__name__)
   app.config["SECRET_KEY"] = "change-this-in-production"
   app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

   exts = ExtensionManager()
   exts.init_app(app)

   with app.app_context():
       db.create_all()

   if __name__ == "__main__":
       app.run(debug=True)

Run this and visit ``http://localhost:5000/admin/`` to see the admin panel.

Configuration
-------------

Flask-Exts uses Flask's standard configuration system. Key settings:

.. code-block:: python

   # Required
   SECRET_KEY = "your-secret-key"
   SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"

   # Security (for JWT-based API auth)
   JWT_SECRET_KEY = "your-jwt-secret-at-least-32-bytes!"
   JWT_HASH = "HS256"

   # Admin panel access control
   ADMIN_ALLOW_ACCESS = True  # Set False to require login

   # Internationalization
   BABEL_DEFAULT_LOCALE = "en"
   BABEL_DEFAULT_TIMEZONE = "UTC"

   # CSRF Protection
   CSRF_ENABLED = True

Building a Complete Application
-------------------------------

Let's build a blog application with user authentication and admin panel.

Step 1: Define Models
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # models.py
   from typing import Optional, List
   from datetime import datetime
   from flask_exts.datastore.sqla import db
   from sqlalchemy.orm import Mapped, mapped_column, relationship
   from sqlalchemy import ForeignKey

   class Category(db.Model):
       __tablename__ = "categories"
       id: Mapped[int] = mapped_column(primary_key=True)
       name: Mapped[str]
       posts: Mapped[List["Post"]] = relationship(back_populates="category")

       def __str__(self):
           return self.name

   class Post(db.Model):
       __tablename__ = "posts"
       id: Mapped[int] = mapped_column(primary_key=True)
       title: Mapped[str]
       content: Mapped[str]
       created_at: Mapped[datetime] = mapped_column(default=datetime.now)
       category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
       category: Mapped[Optional["Category"]] = relationship(back_populates="posts")

       def __str__(self):
           return self.title

Step 2: Create Admin Views
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # views.py
   from flask_exts.admin.sqla.view import SqlaModelView
   from flask_exts.admin.model.form import InlineForm
   from models import Post, Category

   class CategoryView(SqlaModelView):
       # Inline editing: edit Posts directly inside Category form
       inline_models = (
           InlineForm(Post, form_columns=("title", "content")),
       )

   class PostView(SqlaModelView):
       column_list = ["id", "title", "category", "created_at"]
       column_searchable_list = ["title", "content"]
       column_filters = ["category.name", "created_at"]
       column_editable_list = ["title"]
       can_export = True

Step 3: Wire It All Together
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # app.py
   from flask import Flask
   from flask_exts import ExtensionManager
   from flask_exts.datastore.sqla import db
   from models import Category, Post
   from views import CategoryView, PostView

   def create_app():
       app = Flask(__name__)
       app.config["SECRET_KEY"] = "dev"
       app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

       exts = ExtensionManager()
       exts.init_app(app)

       # Register admin views
       exts.admin.register_view(CategoryView(Category))
       exts.admin.register_view(PostView(Post))

       with app.app_context():
           db.create_all()

       return app

   if __name__ == "__main__":
       app = create_app()
       app.run(debug=True)

Step 4: Create an Admin User
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the built-in CLI commands:

.. code-block:: console

   flask security create_admin mypassword

This creates a user ``admin`` with the ``admin`` role and password ``mypassword``.

Other CLI commands:

.. code-block:: console

   flask datastore create_all          # Create database tables
   flask security create_user alice    # Create a regular user

User Authentication
-------------------

Flask-Exts provides a complete user center with:

- Login / Logout
- Registration
- Password reset (via email)
- Email verification
- Two-factor authentication (TOTP)
- Recovery codes

When ``ADMIN_ALLOW_ACCESS = False``, the admin panel requires login.
Users with the ``admin`` role get full access to the admin panel.

Visit ``/user/login`` to access the login page, ``/user/register`` for registration.

Admin Panel Features
--------------------

The ``SqlaModelView`` provides rich CRUD functionality:

.. code-block:: python

   class MyModelView(SqlaModelView):
       # Columns shown in list view
       column_list = ["id", "name", "email", "created_at"]

       # Enable search on specific columns
       column_searchable_list = ["name", "email"]

       # Add filter dropdowns
       column_filters = ["name", "created_at"]

       # Make columns editable inline (in list view)
       column_editable_list = ["name"]

       # Control which columns appear in create/edit forms
       form_columns = ["name", "email"]

       # Exclude columns from forms
       form_excluded_columns = ["created_at"]

       # Enable CSV/XLS export
       can_export = True

       # Enable modal dialogs for create/edit
       create_modal = True
       edit_modal = True

       # Pagination settings
       page_size = 20
       can_set_page_size = True

       # Inline models (edit related models in the same form)
       inline_models = (RelatedModel,)

Custom Views
~~~~~~~~~~~~

You can create custom admin views that don't map to a database model:

.. code-block:: python

   from flask_exts.admin import View, expose_url

   class DashboardView(View):
       @expose_url("/")
       def index(self):
           return self.render("dashboard.html")

   exts.admin.register_view(DashboardView(name="Dashboard", url="dashboard"))

Internationalization
--------------------

Flask-Exts uses Flask-Babel for i18n. Configure supported languages:

.. code-block:: python

   app.config["BABEL_ACCEPT_LANGUAGES"] = "en;zh_CN;fr"
   app.config["BABEL_DEFAULT_LOCALE"] = "zh_CN"

Built-in translations are provided for English (en) and Chinese (zh_CN).

Next Steps
----------

- See :doc:`configure` for full configuration reference
- See :doc:`examples` for the demo application with sample data
- See :doc:`api` for API documentation
