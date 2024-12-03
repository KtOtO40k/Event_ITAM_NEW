from anyio import current_time
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from contextlib import contextmanager
from EventPlaner.RandomServise import event_id_make
from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from fastapi import HTTPException
from sqlalchemy import DateTime
from datetime import datetime
from sqlalchemy import LargeBinary
from fastapi import File, UploadFile


Base = declarative_base()

# таблица для связи
user_event_association = Table(
    'user_event_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('event_id', String, ForeignKey('events.id'), primary_key=True)
)

# модель для мероприятий
class Event(Base):
    __tablename__ = 'events'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    start = Column(DateTime, nullable=True)
    stop = Column(DateTime, nullable=True)
    count = Column(Integer, nullable=True)
    tags = Column(String, nullable=True)
    image = Column(LargeBinary, nullable=True)
    users = relationship('Users', secondary=user_event_association, back_populates='events')


# модель для пользователей
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    second_name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    number_group = Column(String, nullable=True)
    age = Column(String, nullable=True)
    events = relationship('Event', secondary=user_event_association, back_populates='users')
# модель админов
class Admins(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)

engine = create_engine(
    'sqlite:///C:/Users/co730/PycharmProjects/EventPlanerITAM/.venv/EventPlaner/database.db'
)
Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    finally:
        session.close()

# функция для создания мероприятия
def create_event(id,name, start, stop, count, tags):
    try:
        start_datetime = datetime.strptime(start, "%Y-%m-%d %H:%M")
        stop_datetime = datetime.strptime(stop, "%Y-%m-%d %H:%M")
    except(ValueError):
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте формат 'YYYY-MM-DD HH:MM'.")
    with get_session() as session:
        new_event = Event(
            id=id,
            name=name,
            start=start_datetime,
            stop=stop_datetime,
            count=count,
            tags=tags
        )
        session.add(new_event)

# функция для создания пользователя
def create_user(name, second_name, surname, number_group, age):
    with get_session() as session:
        new_user = Users(
            name=name,
            second_name=second_name,
            surname=surname,
            number_group=number_group,
            age=age
        )
        session.add(new_user)

# получение всех мероприятий, на которые записан пользователь
def read_user_events(user_id):
    with get_session() as session:
        user = session.query(Users).filter(Users.id == user_id).first()
        if not user:
            return f"Пользователь с ID {user_id} не найден."
        return [event.name for event in user.events]

# получение всех пользователей, записанных на мероприятие
def read_event_users(event_id):
    with get_session() as session:
        event = session.query(Event).filter(Event.id == event_id).first()
        if not event:
            return f"Мероприятие с ID {event_id} не найдено."
        return [f"{user.name} {user.surname}" for user in event.users]

# присоединение пользователя к мероприятию
def join_user_to_event(user_id, event_id):
    with get_session() as session:
        user = session.query(Users).filter(Users.id == user_id).first()
        event = session.query(Event).filter(Event.id == event_id).first()
        if not user:
            return f"Пользователь с ID {user_id} не найден."
        if not event:
            return f"Мероприятие с ID {event_id} не найдено."
        temp = event.count
        temp2 = event.start
        temp3 = event.stop
        cur_time = datetime.now()
        if ((temp>0)and(temp2 >= cur_time)and(temp3 >= cur_time)):
            temp=temp-1
            event.count = temp
            event.users.append(user)
            return f"Вы записаны на {event.name}."
        else:
            return f"Запись на мероприятие закрыта."


# присвоение пользователю статуса админа
def user_to_admin(user_id):
    with get_session() as session:
        new_admin = Admins(id = user_id)
        session.add(new_admin)
# прорверка админ ли юзер
def read_admin_or_not(user_id):
    with get_session() as session:
        admin = session.query(Admins).filter(Admins.id == user_id).first()
        if not admin:
            raise HTTPException(status_code=404)
            return f"Пользователь с ID {user_id} не является администратором."
        raise HTTPException(status_code=200)
# обновление данных пользователя
def update_user(user_id: int, updates: dict):
    with get_session() as session:
        user = session.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"Пользователь с ID {user_id} не найден.")
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise HTTPException(status_code=400, detail=f"Поле {key} не существует.")
    return {"message": "Данные успешно обновлены"}

#обновление данных мероприятия
def update_event(event_id: str, updates: dict):
    with get_session() as session:
        event = session.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail=f"Мероприятие с ID {event_id} не найдено.")
        for key, value in updates.items():
            if hasattr(event, key):
                setattr(event, key, value)
            else:
                raise HTTPException(status_code=400, detail=f"Поле {key} не существует.")
        return {"message": "Данные успешно обновлены"}
#удаление пользователя из списка администраторов
def delete_admin(user_id: int):
    with get_session() as session:
        user = session.query(Admins).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"Пользователь с ID {user_id} не найден.")
        session.delete(user)
    return {"message": "Данные успешно обновлены"}

#отмена записи
from sqlalchemy import and_
def leave_event(user_id: int, event_id: str):
    with get_session() as session:
        association = session.query(user_event_association).filter(
            and_(
                user_event_association.c.user_id == user_id,
                user_event_association.c.event_id == event_id
            )
        ).first()
        if not association:
            raise HTTPException(status_code=404, detail="Связь между пользователем и мероприятием не найдена.")

        session.execute(user_event_association.delete().where(
            and_(
                user_event_association.c.user_id == user_id,
                user_event_association.c.event_id == event_id
            )
        ))
    return {"message": "Пользователь успешно покинул мероприятие"}

def update_event_image(event_id: str, image):
    with get_session() as session:
        event = session.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail=f"Мероприятие с ID {event_id} не найдено.")
        event.image = image
        return {"message": "Данные успешно обновлены"}


#Event.__table__.drop(engine)
#Users.__table__.drop(engine)