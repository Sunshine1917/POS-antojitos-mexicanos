from collections import defaultdict 
from errores import ErrorIdNoEncontrado, ErrorPadreInexistente

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
          suma_modificadores += mod["PrecioExtraHistorico"]

     suma_hijos = 0
     for hijo in nodo["Contiene"]:
          suma_hijos += calcular_precio_nodo(hijo)

     total = (precio_base + suma_modificadores + suma_hijos) * nodo["Cantidad"]
     return total
