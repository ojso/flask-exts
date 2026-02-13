from sqlalchemy import inspect


def get_identity(instance):
    """
    Return primary key values from an instance.
    """
    identity = inspect(instance).identity
    if len(identity) == 1:
        return identity[0]
    else:
        return identity
