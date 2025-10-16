from datetime import datetime
from typing import Optional

from ...datastore.sqla import db
from ...datastore.sqla.orm import Mapped
from ...datastore.sqla.orm import mapped_column
from ...datastore.sqla.orm import LargeBinary
from ...datastore.sqla.orm import ForeignKey
from ...datastore.sqla.orm import relationship
from ...datastore.sqla.orm import JSON
from ...datastore.sqla.orm import MutableList


class WebAuthnMixin(db.Model):
    __tablename__ = "webauthn"

    id: Mapped[int] = mapped_column(primary_key=True)
    credential_id: Mapped[bytes] = mapped_column(
        LargeBinary(1024), index=True, unique=True
    )
    public_key: Mapped[bytes] = mapped_column(LargeBinary)
    sign_count: Mapped[Optional[int]] = mapped_column(default=0)
    transports: Mapped[Optional[list[str]]] = mapped_column(
        type_=MutableList.as_mutable(JSON)
    )
    backup_state: Mapped[bool] = mapped_column()
    device_type: Mapped[str] = mapped_column()
    extensions: Mapped[Optional[str]] = mapped_column()
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
