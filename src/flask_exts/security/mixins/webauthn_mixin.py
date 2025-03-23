class WebAuthnMixin:

    def get_user_mapping(self):
        """
        Return the filter needed by find_user() to get the user
        associated with this webauthn credential.
        Note that this probably has to be overridden when using mongoengine.
        """
        return dict(id=self.user_id)
