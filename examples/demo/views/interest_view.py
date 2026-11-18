from flask import request
from flask_login import current_user
from sqlalchemy import select

from flask_exts.admin.sqla.view import SqlaModelView
from flask_exts.datastore.sqla import db
from flask_exts.security.authorizer.rbac_authorizer import Authenticated, Predicate

from ..models.user_interest import UserInterest


def owns_interest(ctx):
    """Allow the action only when the target row belongs to ``ctx.user``."""
    user_id = getattr(ctx.user, "id", None)
    if user_id is None:
        return False

    # ``edit_view`` reads the id from the query string; ``delete_view`` reads
    # it from the submitted form. Keep the source aligned with the handler so a
    # forged id in the other location cannot pass the check.
    fn_name = getattr(ctx.fn, "__name__", "")
    raw_id = (
        request.form.get("id") if fn_name == "delete_view" else request.args.get("id")
    )
    try:
        interest_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        return False
    if interest_id is None:
        return False

    interest = db.session.get(UserInterest, interest_id)
    return interest is not None and interest.user_id == user_id


def has_no_interest(ctx):
    """Allow creation only while the user has no interest row yet."""
    user_id = getattr(ctx.user, "id", None)
    if user_id is None:
        return False
    existing = db.session.scalar(
        select(UserInterest.id).where(UserInterest.user_id == user_id)
    )
    return existing is None


class InterestView(SqlaModelView):
    """Show every user's interest; let each user edit only their own."""

    column_list = ("id", "user.username", "content")
    column_labels = {"user.username": "User", "content": "Interests"}  # noqa: RUF012
    column_searchable_list = ("user.username", "content")
    column_default_sort = ("id", False)
    # Owner is assigned on create and can never be changed through the form.
    form_columns = ("content",)

    # The demo only demonstrates editing; delete stays disabled.
    can_delete = False
    action_disallowed_list = ("delete",)

    # Any logged-in user may read every row. Per-method requirements below
    # replace this default for the write actions.
    permission = Authenticated()
    permissions = {  # noqa: RUF012
        "create_view": Predicate(has_no_interest),
        "edit_view": Predicate(owns_interest),
    }

    def create_model(self, model):
        """Assign the current user as owner before saving."""
        model.user_id = current_user.id
        return super().create_model(model)


interestview = InterestView(UserInterest, name="Interest", endpoint="interest")
