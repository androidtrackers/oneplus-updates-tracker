"""OnePlus Updates Tracker Database initialization"""
import logging

from sqlalchemy import (Column, Integer, MetaData, String, Table,
                        create_engine, inspect)
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import sessionmaker

from op_tracker import CONFIG, WORK_DIR

logger = logging.getLogger(__name__)
engine: Engine = create_engine(
    f"sqlite:///{WORK_DIR}/{CONFIG.get('db')}.db",
    connect_args={"check_same_thread": False},
)
logger.info(f"Connected to {engine.name} database at {engine.url}")
connection: Connection = engine.connect()

# Create a MetaData instance
metadata: MetaData = MetaData()
# reflect db schema to MetaData
metadata.reflect(bind=engine)
# check if the table exists
ins = inspect(engine)
if "updates" not in ins.get_table_names():
    logger.info("Updates table not found, creating one")
    posts = Table(
        "updates",
        metadata,
        Column("id", Integer(), primary_key=True, autoincrement=True),
        Column("device", String(), nullable=False),
        Column("region", String(), nullable=False),
        Column("version", String(), nullable=False),
        Column("branch", String(), nullable=False),
        Column("type", String(), nullable=False),
        Column("size", String(), nullable=False),
        Column("md5", String(32), nullable=False, unique=True),
        Column("filename", String(), nullable=False, unique=True),
        Column("link", String(), nullable=False, unique=True),
        Column("date", String(), nullable=False),
        Column("changelog", String(), nullable=False),
        Column("changelog_link", String()),
        Column("product", String()),
        Column("insert_date", String()),
    )
    metadata.create_all(engine)
    Session: sessionmaker = sessionmaker(bind=engine)
    session: Session = Session()
else:
    Session: sessionmaker = sessionmaker(bind=engine)
    session = Session()
