from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from collections import defaultdict 
from dotenv import load_dotenv
from typing import Annotated 
from pathlib import Path
import datetime as dt
import sqlite3
import os

load_dotenv()
db_name = os.getenv("DB_NAME", "antojitos_mexicanos.db")
ruta = Path(__file__).resolve().parent.parent / db_name

# CLASES para Orden
class Pedido(BaseModel):
     Platillo: int = Field(gt = 0)
     Cantidad: int = Field(ge = 1)
     Modificador: list[int] = []
     Nota: str | None = None
     Contiene: list['Pedido'] = []

class Orden(BaseModel): 
     NombreCliente: str = Field(min_length= 1)
     Platillos: list['Pedido'] = Field(min_length= 1)

class OrdenRespuesta(BaseModel): #Modelo de respuesta
     Message: str
     OrdenID: int
     Total: int

# Clases para generar la Comanda
class ModificadoresItem(BaseModel):
     NombreModificador: str
     Cantidad: int

class Comanda(BaseModel):
     Cantidad: int = Field(gt = 0)
     NombrePlatillo: str = Field(min_length= 1)
     Modificadores: list['ModificadoresItem'] = []
     Notas: str | None = None
     Contiene: list['Comanda'] = []

class ComandaRespuesta(BaseModel):
     OrdenID: int = Field(gt = 0)
     FechaPeticion: dt.datetime
     NombreCliente:str = Field(min_length= 1)
     Platillos: list['Comanda'] = Field(min_length=1)

# Clases para generar el ticket
class Ticket(BaseModel):
     Cantidad: int = Field(gt=0)
     NombrePlatillo:str = Field(min_lenght= 1)
     Modificadores: list['ModificadoresItem'] = []
     Contiene: list['Ticket'] = []

class TicketRaiz(Ticket):
     PrecioTotalPlatillo: int = Field(ge= 0)

class TicketRespuesta(BaseModel):
     OrdenID: int = Field(gt = 0)
     FechaPeticion: dt.datetime
     NombreCliente: str = Field(min_length=1)
     Platillos: list['TicketRaiz'] = Field(min_length=1)
     Total: int = Field(gt= 0)

# MANEJO DE ERRORES
class ErrorIdNoEncontrado(Exception):
     def __init__(self,tipo_articulo,campo,mensaje):
          self.tipo_articulo = tipo_articulo
          self.campo = campo
          self.mensaje = mensaje
          super().__init__(f"{mensaje} : Tipo '{tipo_articulo}', ID enviado: {campo} ")
class ErrorPadreInexistente(Exception):
     def __init__(self,detalle_id,padre_id):
          self.detalle_id = detalle_id
          self.padre_id = padre_id
          self.mensaje = f"Dato corrupto: El hijo {detalle_id} busca al padre {padre_id}, pero no existe"
          super().__init__(self.mensaje)

# FUNCIONES
def adapt_datetime_iso(val):
    return val.replace(tzinfo=None).isoformat()

def convert_datetime(val):
    return dt.datetime.fromisoformat(val.decode())

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

sqlite3.register_adapter(dt.datetime, adapt_datetime_iso)
sqlite3.register_converter("DATETIME", convert_datetime)

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

def ensamblaje_primera_pasada(cursor, orden_id: int):
     consulta_detalles = '''
          SELECT OD.DetalleID,
                 OD.DetallePadreID,
                 OD.Cantidad,
                 OD.PrecioBaseHistorico,
                 OD.Notas,
                 P.Name AS NombrePlatillo
          FROM ORDEN_DETALLADO OD
          INNER JOIN PLATILLO P ON OD.PlatilloID = P.PlatilloID
          WHERE OD.OrdenID = ?
          ORDER BY OD.DetalleID ASC;
     '''
     cursor.execute(consulta_detalles, (orden_id,))
     filas_detalles = cursor.fetchall()

     if not filas_detalles:
          raise ErrorIdNoEncontrado("Orden", orden_id, "La orden solicitada no existe en el historial")

     consultar_modificadores = '''
          SELECT ODM.DetalleID,
                 ODM.PrecioExtraHistorico,
                 ODM.Cantidad,
                 M.Name AS NombreModificador
          FROM ORDEN_DETALLE_MODIFICADOR ODM
          INNER JOIN MODIFICADOR M ON ODM.ModificadorID = M.ModificadorID
          INNER JOIN ORDEN_DETALLADO OD ON ODM.DetalleID = OD.DetalleID
          WHERE OD.OrdenID = ?
     '''
     cursor.execute(consultar_modificadores, (orden_id,))
     filas_modificadores = cursor.fetchall()

     dic_modificadores = defaultdict(list)

     for mod in filas_modificadores:
          detalle_id = mod["DetalleID"]
          dic_modificadores[detalle_id].append({
               "NombreModificador": mod["NombreModificador"],
               "PrecioExtraHistorico": mod["PrecioExtraHistorico"],
               "Cantidad": mod["Cantidad"]
          })

     dic_nodos = {}

     for fila in filas_detalles:
          detalle_id = fila["DetalleID"]
          nodo = {
               "DetalleID": detalle_id,
               "DetallePadreID": fila["DetallePadreID"],
               "NombrePlatillo": fila["NombrePlatillo"],
               "Cantidad": fila["Cantidad"],
               "PrecioBaseHistorico": fila["PrecioBaseHistorico"],
               "Notas": fila["Notas"],
               "Modificadores": dic_modificadores.get(detalle_id,[]),
               "Contiene": []
          }
          dic_nodos[detalle_id] = nodo

     return dic_nodos

def ensamblaje_segunda_pasada(dic_nodos):
     raices = []
     for detalle_id, nodo in dic_nodos.items():
          padre_id = nodo["DetallePadreID"]
          if padre_id is None:
               raices.append(nodo)

          else:
               if padre_id not in dic_nodos :
                    raise ErrorPadreInexistente(detalle_id, padre_id)
               dic_nodos[padre_id]["Contiene"].append(nodo)

     return raices

def calcular_precio_nodo(nodo):
     precio_base = nodo["PrecioBaseHistorico"]

     suma_modificadores = 0
     for mod in nodo["Modificadores"]:
          suma_modificadores += (mod["PrecioExtraHistorico"]*mod["Cantidad"])

     suma_hijos = 0
     for hijo in nodo["Contiene"]:
          suma_hijos += calcular_precio_nodo(hijo)

     total = (precio_base + suma_modificadores + suma_hijos) * nodo["Cantidad"]
     return total


# Router Orden
router = APIRouter(prefix="/ordenes",
                   tags=["ordenes"],
                   responses= {404:{"message": "Do not found"}})

#END POINTS
@router.post("/", response_model = OrdenRespuesta, status_code = 201)
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
              status_code= 500, detail = "Error interno del servidor"
         )

    finally:
         if not exito:
              cursor.connection.rollback()

@router.get("/{orden_id}/comanda", response_model = ComandaRespuesta, status_code = 200)
def generar_comanda(orden_id: int, cursor: Annotated[sqlite3.Cursor, Depends(get_db)]):
     try:
          cursor.execute("SELECT NombreCliente, FechaHora FROM ORDEN WHERE OrdenID=?;", (orden_id,))
          row = cursor.fetchone()
          if row is None:
               raise ErrorIdNoEncontrado("Orden", orden_id, "La orden solicitada no existe")

          dic_nodos = ensamblaje_primera_pasada(cursor, orden_id)
          raices = ensamblaje_segunda_pasada(dic_nodos)
          return {
               "OrdenID": orden_id,
               "FechaPeticion": row['FechaHora'],
               "NombreCliente": row['NombreCliente'],
               "Platillos": raices
          }
     
     except ErrorIdNoEncontrado as e:
          raise HTTPException(status_code = 404, detail= e.mensaje)
     except ErrorPadreInexistente as e:
          print(f"Log interno: {e.mensaje}")
          raise HTTPException(status_code = 500, detail= "Error interno del servidor")
     except Exception as e:
          print(f"Ocurrio un error imprevisto: {e}")
          raise HTTPException(
               status_code= 500, detail = "Error interno del servidor"
               )

@router.get("/{orden_id}/ticket", response_model= TicketRespuesta, status_code=200)
def generar_ticket(orden_id :int, cursor: Annotated[sqlite3.Cursor, Depends(get_db)]):
     try:
          cursor.execute("SELECT NombreCliente, FechaHora, Total FROM ORDEN WHERE OrdenID=?;", (orden_id,))
          row = cursor.fetchone()
          if row is None:
               raise ErrorIdNoEncontrado("Orden", orden_id, "La orden solicitada no existe")

          dic_nodos = ensamblaje_primera_pasada(cursor, orden_id)
          raices = ensamblaje_segunda_pasada(dic_nodos)

          for raiz in raices:
               raiz["PrecioTotalPlatillo"] = calcular_precio_nodo(raiz)
          return{
               "OrdenID": orden_id,
               "FechaPeticion": row['FechaHora'],
               "NombreCliente": row["NombreCliente"],
               "Platillos": raices,
               "Total": row['Total']
          }
     
     except ErrorIdNoEncontrado as e:
          raise HTTPException(status_code = 404, detail = e.mensaje)
     except ErrorPadreInexistente as e:
          print(f"Log interno: {e.mensaje}")
          raise HTTPException(status_code = 500, detail = "Error interno del servidor")
     except Exception as e:
          print(f"Ocurrio un error imprevisto: {e}")
          raise HTTPException(
               status_code = 500, detail = "Error interno del servidor"
          )