
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