import string
import random

from sqlalchemy import (
    create_engine,
    select,
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy_utils import database_exists


Base = declarative_base()


class Topic(Base):
    __tablename__ = "topic"

    name = Column(String, primary_key=True)
    last_read = Column(Integer)


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    topic_name = Column(String, ForeignKey("topic.name"))
    author = Column(String)
    message = Column(String)


engine = create_engine("sqlite:///BotManager.db")
if not database_exists(engine.url):
    Base.metadata.create_all(engine)


class Database:
    @staticmethod
    def is_topic(name):
        with Session(engine) as session:
            stmt = select(Topic).where(Topic.name == name)
            return session.scalars(stmt).first() is not None

    @staticmethod
    def create_topic(name):
        with Session(engine) as session:
            session.add(Topic(name=name, last_read=-1))
            session.commit()

    @staticmethod
    def get_list_of_topics():
        with Session(engine) as session:
            return [topic[0] for topic in session.query(Topic.name).all()]

    @staticmethod
    def send_message(name, author, message):
        with Session(engine) as session:
            session.add(Message(
                    topic_name=name,
                    author=author,
                    message=message))
            session.commit()

    @staticmethod
    def has_user(user):
        with Session(engine) as session:
            stmt = select(Message.author).where(Message.author == user)
            return session.scalars(stmt).first() is not None

    @staticmethod
    def get_unread_messages(topic_name):
        with Session(engine) as session:
            last_read = session.query(Topic.last_read).filter(Topic.name == topic_name).first()[0]
            messages = session.query(Message).filter((Message.topic_name == topic_name) & (Message.id > last_read)).all()

            if messages:
                session.query(Topic).filter(Topic.name == topic_name).update({'last_read': messages[-1].id})
                session.commit()

            return [message.message for message in messages]
