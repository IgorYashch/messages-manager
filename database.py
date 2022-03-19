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
    code = Column(String, unique=True)


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
    def is_topic_code(code):
        with Session(engine) as session:
            stmt = select(Topic).where(Topic.code == code)
            return session.scalars(stmt).first() is not None

    @staticmethod
    def is_topic_name(name):
        with Session(engine) as session:
            stmt = select(Topic).where(Topic.name == name)
            return session.scalars(stmt).first() is not None

    @staticmethod
    def create_topic(name) -> string:
        #code = "".join(
        #    random.choice(string.ascii_lowercase + string.digits) for _ in range(5)
        #)
        code = "sfu23"  # TODO
        with Session(engine) as session:
            topic = Topic(name=name, code=code)  # TODO: Retry if not unique
            session.add_all([topic])
            session.commit()

        return code

    @staticmethod
    def send_message(topic_code, message):
        with Session(engine) as session:
            stmt = select(Topic.name)  #.where(Topic.code == topic_code)  # TODO: search
            topic_name = session.scalars(stmt).first()

            message = Message(
                    topic_name = topic_name,
                    author = "user",
                    message = message)
            session.add_all([message])
            session.commit()

    @staticmethod
    def get_messages(topic_name, n):
        with Session(engine) as session:
            stmt = select(Message).where(Message.topic_name == topic_name)
            return [message.message for message in session.scalars(stmt)]
