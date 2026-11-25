from flask_login import current_user
from sqlalchemy import select

from flask_exts.admin.sqla.view import SqlaModelView
from flask_exts.datastore.sqla import db
from flask_exts.security.authorizer.rbac_authorizer import Authenticated, Predicate

from ..models.user_interest import UserInterest


def owns_interest(ctx):
    """Allow the action only when the resolved row belongs to ``ctx.user``."""
    user_id = getattr(ctx.user, "id", None)
    obj = getattr(ctx, "object", None)
    if user_id is None or obj is None:
        return False
    return getattr(obj, "user_id", None) == user_id


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
    """Show every user's interest; let each user manage only their own."""

    column_list = ("id", "user.username", "content")
    column_labels = {"user.username": "User", "content": "Interests"}  # noqa: RUF012
    column_searchable_list = ("user.username", "content")
    column_default_sort = ("id", False)
    # Owner is assigned on create and can never be changed through the form.
    form_columns = ("content",)
    column_editable_list = ("content",)
    can_delete = True
    # Row deletion is enabled; bulk delete stays disabled.
    action_disallowed_list = ("delete",)

    # Any logged-in user may read every row. Write entry points are authorized
    # per record through ``object_requirements`` below.
    permission = Authenticated()
    permissions = {"create_view": Predicate(has_no_interest)}  # noqa: RUF012
    object_requirements = {  # noqa: RUF012
        "edit_view": Predicate(owns_interest),
        "delete_view": Predicate(owns_interest),
        "ajax_update": Predicate(owns_interest),
    }

    def create_model(self, model):
        """Assign the current user as owner before saving."""
        model.user_id = current_user.id
        return super().create_model(model)


interestview = InterestView(UserInterest, name="Interest", endpoint="interest")
