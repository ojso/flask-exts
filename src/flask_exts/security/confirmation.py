from datetime import datetime
from flask import url_for
from ..proxies import _security
from ..proxies import _usercenter
from ..email.send import send_mail


class EmailConfirmation:
    """
    Class to handle email confirmation functionality.
    This class provides methods to generate confirmation tokens and
    confirm email addresses based on those tokens.
    """

    def __init__(self):
        pass

    def generate_email_confirmation_token(self, user):
        """Generates a confirmation token for the specified user.
        :param user: The user to work with
        """
        data = (str(user.get_identity()), _security.hasher.hash(user.email))
        token = _security.serializer.dumps("confirm", data)
        return token

    def send_email_confirmation_token(self, user):
        """Sends the confirmation instructions email for the specified user.

        :param user: The user to send the instructions to
        """

        token = self.generate_email_confirmation_token(user)
        link = url_for("user.email_confirm", token=token, _external=True)

        send_mail(
            "email_confirmation",
            user.email,
            user=user,
            confirmation_link=link,
            confirmation_token=token,
        )

    def confirm_email_token(token, within=None):
        """
        View function which handles an email confirmation request.
        This is always a GET from an email - so for 'spa' must always redirect.
        """
        if within is None:
            within = _security.get_within("confirm")

        expired, invalid, token_data = _security.serializer.loads(
            "confirm", token, within
        )

        if expired:
            return ("expired", None)
        
        if invalid or not token_data:
            return ("invalid_token", None)

        token_user_identity, token_email_hash = token_data
        user = _usercenter.find_user(token_user_identity)

        if not user:
            return ("no_user", None)

        if not _security.hasher.verify_hash(user.email, token_email_hash):
            return ("invalid_email", None)

        if user.email_verified:
            return ("already_confirmed", user)
        
        user.email_verified = True
        user.email_verified_at = datetime.now()

        _usercenter.save_user(user)
        
        return ("confirmed", user)
    
        _datastore.put(user)
        user_confirmed.send(
            current_app._get_current_object(),
            _async_wrapper=current_app.ensure_sync,
            user=user,
        )

        after_this_request(view_commit)
        m, c = get_message("EMAIL_CONFIRMED")

        # ? The only case where user is logged in already would be if
        # LOGIN_WITHOUT_CONFIRMATION
        if user != current_user:
            logout_user()
            if cv("AUTO_LOGIN_AFTER_CONFIRM"):
                # N.B. this is a (small) security risk if email went to wrong place.
                # and you have the LOGIN_WITHOUT_CONFIRMATION flag since in that case
                # you can be logged in and doing stuff - but another person could
                # get the email.
                # Note also this goes against OWASP recommendations.
                response = _security.two_factor_plugins.tf_enter(
                    user, False, "confirm", next_loc=propagate_next(request.url, None)
                )
                if response:
                    do_flash(m, c)
                    return response
                login_user(user, authn_via=["confirm"])

        if cv("REDIRECT_BEHAVIOR") == "spa":
            return redirect(
                get_url(
                    cv("POST_CONFIRM_VIEW"),
                    qparams=user.get_redirect_qparams({c: m}),
                )
            )
        do_flash(m, c)
        return redirect(
            get_url(cv("POST_CONFIRM_VIEW"))
            or get_url(
                cv("POST_LOGIN_VIEW") if cv("AUTO_LOGIN_AFTER_CONFIRM") else ".login"
            )
        )
