from pydantic import BaseModel, Field, ConfigDict, PlainSerializer
from typing import Annotated 
import datetime as dt

def centavos_a_pesos(centavos:int) -> str: 
     signo = "-" if centavos < 0 else ""
     pesos, resto = divmod(abs(centavos), 100)
     return f"{signo}{pesos}.{resto:02d}"

Dinero = Annotated[int, PlainSerializer(centavos_a_pesos, return_type= str, when_used="json")]

class Pedido(BaseModel):
     model_config = ConfigDict(extra='forbid')
     Platillo: int = Field(gt = 0)
     Cantidad: int = Field(ge = 1)
     Modificador: list[int] = []
     Notas: str | None = None
     Contiene: list['Pedido'] = []

class Orden(BaseModel): 
     model_config = ConfigDict(extra='forbid')
     NombreCliente: str = Field(min_length= 1)
     Platillos: list['Pedido'] = Field(min_length= 1)

class OrdenRespuesta(BaseModel): #Modelo de respuesta
     Message: str
     OrdenID: int
     Total: Dinero = Field(gt=0)

# Clases para generar la Comanda
class ModificadoresItem(BaseModel):
     NombreModificador: str
     Cantidad: int #Se tomo la decisión de que cantidad siempre valga uno

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
     NombrePlatillo:str = Field(min_length= 1)
     Modificadores: list['ModificadoresItem'] = []
     Contiene: list['Ticket'] = []

class TicketRaiz(Ticket):
     PrecioTotalPlatillo: Dinero = Field(ge= 0)

class TicketRespuesta(BaseModel):
     OrdenID: int = Field(gt = 0)
     FechaPeticion: dt.datetime
     NombreCliente: str = Field(min_length=1)
     Platillos: list['TicketRaiz'] = Field(min_length=1)
     Total: Dinero = Field(gt= 0)