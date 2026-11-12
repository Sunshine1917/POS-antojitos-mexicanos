from errores import ErrorIdNoEncontrado, ErrorPadreInexistente
from schemas.orden import Orden, Pedido, OrdenRespuesta, ComandaRespuesta, TicketRespuesta
from servicios.arbol_orden import (search_platillo, search_modificador,
     ensamblaje_primera_pasada, ensamblaje_segunda_pasada, calcular_precio_nodo)
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated 
from db import get_db
import datetime as dt
import sqlite3

# Router Orden
router = APIRouter(prefix="/ordenes",
                   tags=["ordenes"],
                   responses= {404:{"message": "Do not found"}})

#END POINTS
@router.post("", response_model = OrdenRespuesta, status_code = 201)
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
                             (orden_id, platillo.Platillo, padre_id, platillo.Cantidad, precio_base, platillo.Notas))
              
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

         if precio_total <= 0:
              raise HTTPException(status_code=422,
                                  detail="La orden debe tener un total mayor a cero")
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