import os

from db.db import database

async def create_memory_table():
    sql_file_path = os.path.join(os.path.dirname(__file__), "sql/create_memory_table.sql")
    with open(sql_file_path, "r") as f:
        create_table_query = f.read()
    await database.execute(create_table_query)
    print("[Database] Tabela memory_messages criada ou já existente.")
