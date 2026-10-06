from base import Base
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False) 
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(), nullable=False)