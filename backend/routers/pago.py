from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix = "/pago",
                   tags = ["pago"],
                   responses = {404 : {"message": "Cuenta no encontrada"}})

#Entidad pago 
class Pago(BaseModel):
    id: int
    cliente: str
    orden: int

pago_fake_db = [Pago(id= 1, cliente= "mesa 1", orden= 34),
                Pago(id= 2, cliente= "mesa 2", orden= 124),
                Pago(id= 4, cliente= "doña Lupe", orden= 35)]

@router.get("/{id}")
async def pago(id: int):
    for pago in pago_fake_db:
        if pago.id == id:
            return pago

    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                        detail= "Pago no encontrado")

    

