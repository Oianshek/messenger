from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db import Base
from models.message import Message


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    sent_messages = relationship("Message", foreign_keys=[Message.sender_id], back_populates="sender",
                                 cascade="all, delete")
    received_messages = relationship("Message", foreign_keys=[Message.receiver_id], back_populates="receiver",
                                     cascade="all, delete")
