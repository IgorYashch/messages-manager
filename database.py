from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    MetaData,
    ForeignKey,
)
from sqlalchemy_utils import database_exists


engine = create_engine("sqlite:///BotManager.db", echo=True)
meta = MetaData()

topics = Table(
    "topics",
    meta,
    Column("id", Integer, primary_key=True),
    Column("header", String),
    Column("manager", String),
)

messages = Table(
    "messages",
    meta,
    Column("id", Integer, primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id")),
    Column("sender", String),
    Column("message", String),
)


def get_conn():
    conn = engine.connect()
    if not database_exists(engine.url):
        meta.create_all(engine)

    return conn


if __name__ == "__main__":
    # Tests for empty database
    conn = get_conn()

    # Create topic
    ins = topics.insert().values(header="header", manager="manager")
    topic_id = conn.execute(ins).inserted_primary_key[0]
    print("Create topic", topic_id)

    # Get topic lists
    s = topics.select()
    result = conn.execute(s)
    for row in result.fetchall():
        print(row)

    # Send messages to topic
    for idx in range(3):
        ins = messages.insert().values(
            topic_id=topic_id, sender="sender", message="message " + str(idx)
        )
        conn.execute(ins)

    # Get last 2 messages from topic
    s = (
        messages.select()
        .where(messages.columns.topic_id == topic_id)
        .order_by(messages.columns.id.desc())
        .limit(2)
    )
    result = conn.execute(s)
    for row in result.fetchall()[::-1]:
        print(row)
