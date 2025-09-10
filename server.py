from fastapi import FastAPI
from pydantic import BaseModel
import uuid

class BodyType(BaseModel):
    message:str



class ChatsData(BaseModel):
    id:str
    messages:list[str]


class UserData(BaseModel):
    name:str
    chats:list[ChatsData]

app = FastAPI()


@app.get("/")
def root_route():
    return {
        "hello":"baby"
    }


@app.get("/chat/new")
def root_route():
    uniqueId = uuid.uuid4()
    return {
        "uniqueId":uniqueId
    }


@app.post("/chats/:chatId")
def chat_route(chatId:int,body:BodyType):
   return{
       "body":body.message
   }