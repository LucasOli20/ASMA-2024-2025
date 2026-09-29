import sqlalchemy
from sqlalchemy import Table, Column, Integer, Text, String, DateTime, MetaData, func

metadata = MetaData()

memory = Table(
    "memory",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("text", Text),
    Column("response", Text),
    Column("emotion", Text),
    Column("feedback", Text),
    Column("user_suggestion", Text),  # ⚡ novo campo
)
