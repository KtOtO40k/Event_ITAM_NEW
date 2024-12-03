from EventPlaner.DB import create_event, read_user_events, join_user_to_event, read_event_users, user_to_admin, \
    read_admin_or_not, update_user, update_event, delete_admin, leave_event, update_event_image
from EventPlaner.DB import create_user
from EventPlaner.RandomServise import event_id_make
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import LargeBinary
from fastapi import File, UploadFile
app = FastAPI()


@app.post("/join")
def Joiner(user_id:int, event_id: str):
    return join_user_to_event(user_id,event_id)
    #raise HTTPException(status_code=200)

class EventModel(BaseModel):
    name: str
    start: str
    stop: str
    count: int
    tags: str


@app.post("/create_event")
async def EventCreator(event: EventModel):
    id = event_id_make()
    create_event(id, event.name, event.start, event.stop, event.count, event.tags)

@app.patch("/update_event_image")
async def UpdateEventImage(event_id:str,image: UploadFile = File(...)):
    image_data = await image.read()
    return update_event_image(event_id,image_data)


class UserModel(BaseModel):
    name: str
    second_name: str
    surname: str
    number_group: str
    age: str
@app.post("/create_user")
def EventCreator(user: UserModel):
    create_user(user.name,user.second_name,user.surname,user.number_group,user.age)
@app.get("/read_user_events")
def ReadUserEvents(user_id: int):
    return read_user_events(user_id)
@app.get("/read_event_users")
def ReadEventUsers(event_id: str):
    return read_event_users(event_id)
@app.post("/user_to_admin")
def UserToAdmin(user_id: int):
    user_to_admin(user_id)
@app.get("/read_admin_or_not")
def ReadAdminOrNot(user_id: int):
    return read_admin_or_not(user_id)
@app.patch("/update_user")
def UpdateUser(user_id:int,updates: dict):
    return update_user(user_id,updates)
@app.patch("/update_event")
def UpdateEvent(event_id:str,updates: dict):
    return update_event(event_id,updates)
@app.delete("/delete_admin")
def DeleteAdmin(user_id:int):
    delete_admin(user_id)
@app.delete("/leave_event")
def LeaveEvent(user_id: int,event_id: str):
    return (leave_event(user_id, event_id))





uvicorn.run(app)