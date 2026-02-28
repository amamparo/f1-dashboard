import sqlite3
from typing import List, Dict

import pandas as pd
from pydantic import create_model, Field, BaseModel


def get_all_table_names(conn: sqlite3.Connection) -> List[str]:
    cursor = conn.cursor()
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor.execute(query)

    return [row[0] for row in cursor.fetchall()]


def autogen_models(db: str = 'data.db') -> Dict[str, BaseModel]:
    """Generate Pydantic models for all tables in the SQLite database.

    Args:
        db (str, optional): Path to SQLite DB file. Defaults to 'data.db'.

    Returns:
        Dict[str, BaseModel]: Returns a dictionary where keys are table names and values are Pydantic models.
    """
    conn = sqlite3.connect(db)
    tables = get_all_table_names(conn)
    models = {}

    type_map = {
        'int64': int,
        'float64': float,
        'object': str,
    }

    for table in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        types = {
            k: (type_map[str(v)], Field())
            for k, v in df.dtypes.to_dict().items()
        }
        table_model = create_model(
            f'{"".join(table.replace("_", " ").title().split())}Model',
            **types,
        )
        models[table] = table_model

    return models
