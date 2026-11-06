from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Annotated 
from pathlib import Path
import datetime as dt
import sqlite3
import os

load_dotenv()
db_name = os.getenv("DB_NAME", "antojitos_mexicanos.db")
ruta = Path(__file__).resolve().parent.parent / db_name

# CLASES
class Pedido(BaseModel):
     Platillo: int = Field(gt = 0)
     Cantidad: int = Field(ge = 1)
     Modificador: list[int] = []
     Nota: str | None = None
     Contiene: list['Pedido'] = []

class Orden(BaseModel): 
     NombreCliente: str = Field(min_length= 1)
     Platillos: list['Pedido'] = Field(min_length= 1)

class Respuesta(BaseModel): #Modelo de respuesta
     Message: str
     OrdenID: int
     Total: int

class ErrorIdNoEncontrado(Exception):
     def __init__(self,tipo_articulo,campo,mensaje):
          self.tipo_articulo = tipo_articulo
          self.campo = campo
          self.mensaje = mensaje
          super().__init__(f"{mensaje} : Tipo '{tipo_articulo}', ID enviado: {campo} ")
# FUNCIONES

def adapt_datetime_iso(val):
    return val.replace(tzinfo=None).isoformat()

def convert_datetime(val):
    return dt.datetime.fromisoformat(val.decode())

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def get_db():
    sqlConect = sqlite3.connect(ruta,
                                detect_types = sqlite3.PARSE_DECLTYPES |
                                sqlite3.PARSE_COLNAMES)
    sqlConect.row_factory = dict_factory
    cursor_obj = sqlConect.cursor()
    try:
        yield cursor_obj
    finally:
         if sqlConect:
                cursor_obj.close()
                sqlConect.close()
                print("Conexión a la base de datos cerrada")

def search_platillo(cursor, platillo_id):
     cursor.execute(
          "SELECT PrecioActual FROM PLATILLO WHERE PlatilloID = ?",
          (platillo_id,) 
          )
     row = cursor.fetchone()
     if row is None:
          raise ErrorIdNoEncontrado("Platillo",platillo_id, "El platillo no existe en nuestra base de datos")
     return row["PrecioActual"]

def search_modificador(cursor, modificador_id):
     cursor.execute("SELECT PrecioExtra FROM MODIFICADOR WHERE ModificadorID = ?",
                                       ( modificador_id,))
     row = cursor.fetchone()
     if row is None:
          raise ErrorIdNoEncontrado("Modificador", modificador_id, "El modificador no existe en nuestra base de datos")
     return row["PrecioExtra"]

router = APIRouter(prefix="/pedido",
                   tags=["pedido"],
                   responses= {404:{"message": "Do not found"}})

@router.post("/", response_model = Respuesta, status_code = 201)
def crear_pedido(comanda:Orden, cursor: Annotated[sqlite3.Cursor, Depends(get_db)]):
    exito = False
    try:
         currentTime = dt.datetime.now()
         precio_total = 0
         cursor.execute(
              "INSERT INTO ORDEN (FechaHora, NombreCliente,Total,Estado) VALUES(?,?,?,?);",
              (currentTime,comanda.NombreCliente,precio_total,'Abierta')
         )
         orden_id = cursor.lastrowid

         def desglose_orden(platillo:Pedido, padre_id: int | None, cantidad_real: int):
              nonlocal precio_total
              cantidad =platillo.Cantidad * cantidad_real
              precio_base = search_platillo(cursor, platillo.Platillo)
              precio_total = (precio_base * cantidad) + precio_total

              insert_orden_detallado = '''
                    INSERT INTO ORDEN_DETALLADO (OrdenID,PlatilloID,DetallePadreID,Cantidad, PrecioBaseHistorico, Notas) 
                    VALUES (?,?,?,?,?,?);
                    '''
              cursor.execute(insert_orden_detallado, 
                             (orden_id, platillo.Platillo, padre_id, platillo.Cantidad, precio_base, platillo.Nota))
              
              detalle_id = cursor.lastrowid

              for modificador_id in platillo.Modificador:
                   precio_modificacion = search_modificador(cursor, modificador_id)
                   precio_total = (precio_modificacion * cantidad) + precio_total

                   insert_orden_detalle_modificador = '''
                        INSERT INTO ORDEN_DETALLE_MODIFICADOR (DetalleID,ModificadorID,Cantidad,PrecioExtraHistorico) VALUES (?,?,?,?);
                        '''
                   cursor.execute(insert_orden_detalle_modificador, (detalle_id, modificador_id,1,precio_modificacion))
                   
              for sub_platillos in platillo.Contiene:
                   desglose_orden(sub_platillos,padre_id = detalle_id, cantidad_real = cantidad )
                       
         for platillos in comanda.Platillos:
              desglose_orden(platillos, padre_id=None, cantidad_real = 1)

         cursor.execute(
                            "UPDATE ORDEN SET Total = ?  WHERE OrdenID = ?;",
                            (precio_total,orden_id)
                       )
         cursor.connection.commit()
         exito = True
         return {"Message": "Orden creada exitosamente", "OrdenID": orden_id, "Total": precio_total}

    except ErrorIdNoEncontrado as e:
         raise HTTPException(
              status_code= 422, detail = str(e)
         )
    except HTTPException as e:
         raise e
    
    except sqlite3.Error as e:
         raise HTTPException(status_code=500, detail = f"Error en la base de datos: {e}")

    except Exception as e:
         print(f"Ocurrio un error imprevisto: {e}")
         raise HTTPException(
              status_code= 500, detail = "Error imprevisto en el servidor"
         )

    finally:
         if not exito:
              cursor.connection.rollback()