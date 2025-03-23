from datetime import datetime
from . import db
from . import Mapped
from . import mapped_column
from . import LargeBinary
from . import ForeignKey
from . import relationship
from . import JSON
from ..mixins.webauthn_mixin import WebAuthnMixin


class WebAuthnMixin(db.Model, WebAuthnMixin):
    __tablename__ = "webauthn"

    id: Mapped[int] = mapped_column(primary_key=True)
    credential_id: Mapped[bytes] = mapped_column(
        LargeBinary(1024), index=True, unique=True
    )
    public_key: Mapped[bytes] = mapped_column(LargeBinary)
    sign_count: Mapped[int | None] = mapped_column(default=0)
    transports: Mapped[list[str] | None] = mapped_column(type_=JSON)
    backup_state: Mapped[bool] = mapped_column()
    device_type: Mapped[str] = mapped_column()
    extensions: Mapped[str | None] = mapped_column()
    create_datetime: Mapped[datetime] = mapped_column(default=datetime.now)
    lastuse_datetime: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )
    # name is provided by user - we make sure is unique per user
    name: Mapped[str] = mapped_column()

    # Usage - a credential can EITHER be for first factor or secondary factor
    usage: Mapped[str] = mapped_column()

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="webauthn")
