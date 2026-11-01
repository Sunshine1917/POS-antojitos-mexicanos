import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException,Depends
from pathlib import Path
import sqlite3

load_dotenv
db_name = os.getenv("DB_NAME", "antojitos_mexicanos.db")
ruta = Path(__file__).resolve().parent.parent / db_name

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def get_db():
    sqlConect = sqlite3.connect(ruta)
    sqlConect.row_factory = dict_factory
    cursor_obj = sqlConect.cursor()
    try:
        yield cursor_obj
    finally:
         if sqlConect:
                cursor_obj.close()
                sqlConect.close()
                print("Conexión a la base de datos cerrada")

router = APIRouter(prefix="/menu",
                   tags = ["menu"],
                   responses = {404: {"message": "Do not found"}})

@router.get("/")
def get_menu (cursor = Depends(get_db)):
    try:
         cursor.execute("SELECT * FROM PLATILLO") 
         return cursor.fetchall()
    except sqlite3.Error:
         raise HTTPException(status_code=500,detail="Error al consultar base de datos")