from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime, Boolean
from sqlalchemy.orm import relationship

from db import Base


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    send_date = Column(DateTime(timezone=True), default=datetime.now())
    is_read = Column(Boolean)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
