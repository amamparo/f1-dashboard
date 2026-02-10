from esm_fullstack_challenge.config import DB_FILE
from esm_fullstack_challenge.db import DB


def get_db():
    try:
        db = DB(DB_FILE)
        yield db
    finally:
        pass
