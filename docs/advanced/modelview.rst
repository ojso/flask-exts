ModelView Tutorial
========================

The ``SqlaModelView`` class is the core component for building admin panels with Flask-Exts.
It automatically generates CRUD (Create, Read, Update, Delete) views for your database models
with rich filtering, searching, and customization options.

This view layer is the central admin component in Flask-Exts. It builds CRUD pages for your models
and supports filtering, searching, custom forms, and inline editing.

Basic Setup
-----------

The simplest ModelView requires just a model class:

.. code-block:: python

   from flask_exts.admin.sqla.view import SqlaModelView
   from your_app.models import User

   class UserView(SqlaModelView):
       pass

   # Register with admin
   admin.register_view(UserView(User))

Displaying Columns
------------------

Control which columns appear in the list view using ``column_list``:

.. code-block:: python

   class UserView(SqlaModelView):
       column_list = ['id', 'username', 'email', 'created_at', 'is_active']

For nested columns (relationships), use dot notation:

.. code-block:: python

   class PostView(SqlaModelView):
       column_list = ['id', 'title', 'author.username', 'created_at', 'view_count']

Use ``column_labels`` to customize column headers:

.. code-block:: python

   class PostView(SqlaModelView):
       column_labels = {
           'title': 'Post Title',
           'author.username': "Author's Name",
           'created_at': 'Created Date',
       }

Filtering and Searching
-----------------------

Add search capability to specific columns:

.. code-block:: python

   class UserView(SqlaModelView):
       column_searchable_list = ['username', 'email']

This creates a search box that matches the user's input against these fields.

Add filter dropdowns for specific columns:

.. code-block:: python

   class PostView(SqlaModelView):
       column_filters = ['author.username', 'created_at', 'status']

You can also create custom filter classes for advanced filtering logic:

.. code-block:: python

   from flask_exts.admin.sqla.filter import BaseSQLAFilter
   from flask_exts.admin.sqla.utils import get_model_column_type

   class CustomStatusFilter(BaseSQLAFilter):
       def __init__(self):
           super().__init__(
               column_type=get_model_column_type(Post, "status"),
               column="status",
               name="Status",
               options=[('draft', 'Draft'), ('published', 'Published')]
           )

       def apply(self, query, value):
           if value == 'draft':
               return query.add_filter(self.column, "==", 'draft')
           elif value == 'published':
               return query.add_filter(self.column, "==", 'published')
           return query

   class PostView(SqlaModelView):
       column_filters = [CustomStatusFilter()]

Inline Editing
--------------

Make columns editable directly in the list view:

.. code-block:: python

   class UserView(SqlaModelView):
       column_editable_list = ['username', 'email']

Users can now click on these cells to edit them without opening a separate form.

Form Customization
------------------

Control which fields appear in create/edit forms:

.. code-block:: python

   class UserView(SqlaModelView):
       # Only show these fields
       form_columns = ['username', 'email', 'role']

       # Show everything except these fields
       form_excluded_columns = ['id', 'created_at', 'updated_at']

Customize field behavior with ``form_args``:

.. code-block:: python

   from wtforms import validators

   class UserView(SqlaModelView):
       form_args = {
           'username': {
               'label': 'User Name',
               'validators': [validators.Length(min=3, max=50)],
           },
           'email': {
               'label': 'Email Address',
               'validators': [validators.Email()],
           },
       }

Control widget rendering with ``form_widget_args``:

.. code-block:: python

   class UserView(SqlaModelView):
       form_widget_args = {
           'bio': {'rows': 5},  # Textarea with 5 rows
           'username': {'readonly': True},  # Readonly input
       }

Inline Models
-------------

Edit related models within the parent form (like Django's inline forms):

.. code-block:: python

   from flask_exts.admin.model.form import InlineForm

   class AuthorView(SqlaModelView):
       inline_models = (
           InlineForm(
               Post,
               form_columns=['title', 'content', 'published'],
           ),
       )

Now when editing an Author, users can add/edit/delete Posts directly in the same form.

Sorting and Pagination
----------------------

Set default sorting:

.. code-block:: python

   class PostView(SqlaModelView):
       column_default_sort = [('created_at', True)]  # True = descending

Allow users to change page size:

.. code-block:: python

   class UserView(SqlaModelView):
       page_size = 20
       can_set_page_size = True
       page_size_options = (10, 20, 50, 100)

Row and Batch Operations
------------------------

Allow inline editing of a single column:

.. code-block:: python

   class PostView(SqlaModelView):
       column_editable_list = ['status', 'featured']

Define batch actions (operations on selected records):

.. code-block:: python

   class UserView(SqlaModelView):
       @action('activate', 'Activate Selected')
       def activate_users(self, ids):
           users = User.query.filter(User.id.in_(ids)).all()
           for user in users:
               user.is_active = True
           db.session.commit()

       @action('deactivate', 'Deactivate Selected')
       def deactivate_users(self, ids):
           users = User.query.filter(User.id.in_(ids)).all()
           for user in users:
               user.is_active = False
           db.session.commit()

Define row actions (buttons per row):

.. code-block:: python

   from flask_exts.admin.model.rowaction import ActionFormatter

   class UserView(SqlaModelView):
       row_actions = [
           ActionFormatter(
               lambda v, c, m, p: f'/admin/user/send-email/?id={m.id}',
               'Send Email'
           ),
       ]

Exports
-------

Allow exporting data in multiple formats:

.. code-block:: python

   class UserView(SqlaModelView):
       can_export = True
       export_types = ['csv', 'xls']
       export_max_rows = 1000

Details View Customization
--------------------------

Control which columns appear in the details page:

.. code-block:: python

   class UserView(SqlaModelView):
       column_details_list = [
           'id', 'username', 'email', 'is_active',
           'created_at', 'updated_at', 'last_login'
       ]

Disable certain operations:

.. code-block:: python

   class UserView(SqlaModelView):
       action_disallowed_list = ['delete']  # Users cannot delete via admin
       can_create = False  # Hide create button
       can_edit = True  # Allow edits only

Modal Forms
-----------

Display forms in modals instead of separate pages:

.. code-block:: python

   class UserView(SqlaModelView):
       create_modal = True
       edit_modal = True
       details_modal = True

Complete Example
----------------

A fully-featured ModelView combining most features:

.. code-block:: python

   from flask_exts.admin.sqla.view import SqlaModelView
   from flask_exts.admin.model.form import InlineForm
   from wtforms import validators
   from your_app.models import Author, Post

   class AuthorView(SqlaModelView):
       # List view
       column_list = ['id', 'name', 'email', 'post_count', 'created_at']
       column_searchable_list = ['name', 'email']
       column_filters = ['created_at', 'is_active']
       column_editable_list = ['is_active']
       column_default_sort = ('created_at', True)

       # Inline editing
       inline_models = (InlineForm(Post, form_columns=['title', 'status']),)

       # Form customization
       form_columns = ['name', 'email', 'is_active']
       form_args = {
           'email': {'validators': [validators.Email()]},
           'name': {'validators': [validators.Length(min=3, max=100)]},
       }

       # Features
       can_export = True
       page_size = 20
       can_set_page_size = True
       create_modal = False
       edit_modal = True

       # Labels
       column_labels = {
           'post_count': 'Total Posts',
           'created_at': 'Created Date',
       }

       column_details_list = [
           'id', 'name', 'email', 'post_count',
           'is_active', 'created_at', 'updated_at'
       ]

This view provides:
- Searchable list of authors
- Filterable by creation date and active status
- Inline Post editing
- Form validation for email and name
- CSV/XLS export capability
- 20 rows per page with pagination
- Modal edit forms
- Custom column labels
