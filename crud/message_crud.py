from sqlalchemy.orm import Session

from models.message import Message
from schemas import message_schema


def create_message(db: Session, message: message_schema.MessageCreate, receiver_id: int, sender_id: int):
    db_message = Message(**message.dict(), receiver_id=receiver_id, sender_id=sender_id, is_read=False)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message


def get_multi(db: Session, user_id: int):
    return db.query(Message.sender_id).filter(Message.receiver_id == user_id, Message.is_read == 0).all()


def get_by_sender_and_receiver(db: Session, sender_id: int, receiver_id: int):
    return db.execute("SELECT * FROM messages WHERE (sender_id = :sender_id AND receiver_id = :receiver_id) OR (sender_id = :receiver_id AND receiver_id = :sender_id) ORDER BY send_date", {'sender_id': sender_id, "receiver_id": receiver_id}).all()


def update_message_status(db: Session, sender_id: int, receiver_id: int):
    db.execute("UPDATE messages SET is_read = 1 WHERE (sender_id = :sender_id AND receiver_id = :receiver_id) and is_read = 0", {'sender_id': sender_id, "receiver_id": receiver_id})
    db.commit()
