from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

import core
from db import SessionLocal, engine
from models import user, message
from models.token import Token
from schemas import user_schema, message_schema
from crud import user_crud, message_crud

user.Base.metadata.create_all(bind=engine)
message.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/{user_id}", response_model=user_schema.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# SIMPLE LOGIN WITH JWT TOKEN
@app.post("/login/access-token", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = core.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not db_user:
        raise HTTPException(status_code=404, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=core.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = core.create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# SIMPLE REGISTER
@app.post("/register", response_model=user_schema.User)
def register(user_in: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_crud.create_user(db=db, user=user_in)


# GET MY INFO
@app.get("/users/me/", response_model=user_schema.User)
def read_users_me(current_user: user.User = Depends(core.get_current_user)):
    return current_user


# SEND MESSAGE TO ANOTHER USER
@app.post("/messages/send/{receiver_id}", response_model=message_schema.Message)
def send_message(*, db: Session = Depends(get_db), receiver_id: int, message_in: message_schema.MessageCreate, current_user: user.User = Depends(core.get_current_user)):
    db_user = user_crud.get_user(db, user_id=receiver_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == receiver_id:
        raise HTTPException(status_code=400, detail="CANNOT SEND MESSAGE TO YOURSELF")

    return message_crud.create_message(db=db, message=message_in, receiver_id=receiver_id, sender_id=current_user.id)


# GET ALL UNREAD MESSAGES' SENDERS
@app.get("/messages/get-unread")
def get_unread_messages(*, db: Session = Depends(get_db), current_user: user.User = Depends(core.get_current_user)):
    messages = message_crud.get_multi(db=db, user_id=current_user.id)
    if messages is None:
        return "No messages"

    return messages


# SEE THE CHAT OF SENDERS FROM ENDPOINT ABOVE
@app.get("/messages/chat/{sender_id}")
def read_message(*, db: Session = Depends(get_db), sender_id: int, current_user: user.User = Depends(core.get_current_user)):
    messages = message_crud.get_by_sender_and_receiver(db, sender_id=sender_id, receiver_id=current_user.id)

    if messages is None:
        return "No messages"

    message_crud.update_message_status(db, sender_id=sender_id, receiver_id=current_user.id)

    return messages
