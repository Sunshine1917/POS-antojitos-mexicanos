# db.py
import datetime as dt
import sqlite3
from config import DB_PATH

def adapt_datetime_iso(val):
    return val.replace(tzinfo=None).isoformat()

def _convertir_datetime(val):
    return dt.datetime.fromisoformat(val.decode())

sqlite3.register_adapter(dt.datetime, adapt_datetime_iso)
sqlite3.register_converter("DATETIME", _convertir_datetime)

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def get_db():
    sqlConect = sqlite3.connect(DB_PATH,
                                detect_types = sqlite3.PARSE_DECLTYPES |
                                sqlite3.PARSE_COLNAMES)
    sqlConect.execute("PRAGMA foreign_keys = ON")
    sqlConect.row_factory = dict_factory
    cursor_obj = sqlConect.cursor()
    try:
        yield cursor_obj
    finally:
         if sqlConect:
                cursor_obj.close()
                sqlConect.close()
                print("Conexión a la base de datos cerrada")