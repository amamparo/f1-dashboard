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

    pandas_type_map = {
        'int64': int,
        'float64': float,
        'object': str,
    }

    sqlite_type_map = {
        'INTEGER': int,
        'REAL': float,
        'TEXT': str,
        'BLOB': str,
    }

    for table in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        if len(df) > 0:
            types = {
                k: (pandas_type_map[str(v)], Field())
                for k, v in df.dtypes.to_dict().items()
            }
        else:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            types = {}
            for col in columns:
                col_name = col[1]
                col_type = col[2].upper().split('(')[0].strip()
                py_type = sqlite_type_map.get(col_type, str)
                types[col_name] = (py_type, Field())
        table_model = create_model(
            f'{"".join(table.replace("_", " ").title().split())}Model',
            **types,
        )
        models[table] = table_model

    return models
