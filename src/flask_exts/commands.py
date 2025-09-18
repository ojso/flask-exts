import click
from flask.cli import AppGroup
from .proxies import _userstore
from .datastore.sqla import db


datastore_cli = AppGroup("datastore", short_help="datastore for the app.")


@datastore_cli.command("create_all", help="db.create_all()")
def create_all():
    print(f"datastore create_all ")
    db.create_all()


security_cli = AppGroup("security", short_help="security for the app.")


@security_cli.command("create_user")
@click.argument("name")
def create_user(name):
    print(f"security create_user {name}")
    result = _userstore.create_user(username=name)
    click.echo(result)


@security_cli.command("create_admin", help="create user:admin with admin:role")
@click.argument("password", default="admin")
def create_admin(password):
    u, _ = _userstore.create_user(username="admin", password=password)
    r, _ = _userstore.create_role(name="admin")
    _userstore.user_add_role(u, r)

    print(f"security create admin {u.username} with role {r.name} ")
