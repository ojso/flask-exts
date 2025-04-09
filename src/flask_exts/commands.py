import click
from flask.cli import AppGroup
from flask_exts.proxies import current_usercenter
from flask_exts.datastore.sqla import db


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
    result = current_usercenter.create_user(username=name)
    click.echo(result)


@security_cli.command("create_admin", help="create user:admin with admin:role")
@click.argument("password", default="admin")
def create_admin(password):
    u, _ = current_usercenter.create_user(username="admin", password=password)
    r, _ = current_usercenter.create_role(name="admin")
    current_usercenter.user_add_role(u, r)

    print(f"security create admin {u.username} with role {r.name} ")
