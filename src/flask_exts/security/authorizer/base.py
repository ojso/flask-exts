from abc import ABC, abstractmethod

SESSION_KEY_TFA_VERIFIED = "tfa_verified"
SESSION_KEY_TFA_RECOVERY = "tfa_recovery_login"

#: Holds the id of a user who passed the password check but, because their
#: account has TFA enabled, has not yet completed the TFA step. No login
#: session exists for this user until TFA verification succeeds -- Flask-Login's
#: `login_user` is deliberately not called until then. If the browser leaves
#: this page (closes, lets the session expire, etc.) the pending login is
#: simply abandoned; the user must restart from username/password.
SESSION_KEY_PENDING_TFA_USER_ID = "pending_tfa_user_id"


class Authorizer(ABC):
    @abstractmethod
    def allow(self, *args, **kwargs): ...
