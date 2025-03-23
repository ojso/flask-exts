from typing import Optional, Any


class Identity:
    """Represent the user's identity.

    :param id: The user id
    :param auth_type: The authentication type used to confirm the user's
                      identity.

    The identity is used to represent the user's identity in the system. This
    object is created on login, or on the start of the request as loaded from
    the user's session.

    Once loaded it is sent using the `identity-loaded` signal, and should be
    populated with additional required information.

    Needs that are provided by this identity should be added to the `provides`
    set after loading.
    """

    def __init__(self, id: Optional[Any], auth_type: Optional[str] = None) -> None:
        self.id = id
        self.auth_type = auth_type
        self.provides = set()

    def __repr__(self) -> str:
        return '<{0} id="{1}" auth_type="{2}" provides={3}>'.format(
            self.__class__.__name__, self.id, self.auth_type, self.provides
        )


class AnonymousIdentity(Identity):
    """An anonymous identity"""

    def __init__(self) -> None:
        Identity.__init__(self, None)
