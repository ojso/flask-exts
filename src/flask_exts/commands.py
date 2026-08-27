import click
from flask.cli import AppGroup
from .proxies import current_userstore
from .datastore.sqla import db

datastore_cli = AppGroup("datastore", short_help="datastore for the app.")


@datastore_cli.command("create_all", help="db.create_all()")
def create_all():
    print(f"datastore create_all ")
    db.create_all()


security_cli = AppGroup("security", short_help="security for the app.")


@security_cli.command("create_user")
@click.argument("name")
@click.password_option(
    "--password",
    prompt="Enter password",
    confirmation_prompt=True,
    help="User password (will prompt if not provided)",
)
@click.option("--email", default=None, help="User email address (optional)")
@click.option(
    "--active", is_flag=True, default=False, help="Activate the user immediately"
)
def create_user(name, password, email, active):
    """
    Create a new user with the given NAME.

    Example:
        security create_user john_doe
        security create_user jane --password mypass123 --active
    """
    print(f"security create_user {name}")
    result = current_userstore.create_user(username=name, password=password)
    click.echo(result)


@security_cli.command(
    "create_admin", help="create user:admin(defaullt password:admin) with admin:role"
)
@click.argument("password", default="admin")
def create_admin(password):
    _, user_admin = current_userstore.create_user(username="admin", password=password)
    role_admin = current_userstore.create_role(name="admin")
    current_userstore.user_add_role(user_admin, role_admin)

    print(f"security create admin {user_admin.username} with role {role_admin.name} ")
