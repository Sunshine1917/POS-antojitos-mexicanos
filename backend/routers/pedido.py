from fastapi import APIRouter, HTTPException, exceptions, status
from pydantic import BaseModel

router = APIRouter(prefix= "/pedido",
                   tags= ["pedido"],
                   responses= {404: {"message": "Pedidos no encontrados"}})

#Entidad pedido
class Pedido(BaseModel):
    id: int
    cliente: str
    orden: dict[str, int] # Clave nombre de platillo -> Valor cantidad solicitada

fk_db =[Pedido(id= 1, cliente="Omar", orden = {"chalupa": 4, 
                                               "refresco": 2,
                                               "taco": 5}),

        Pedido(id= 2, cliente= "Karina", orden = {"tostada_simple": 2,
                                                  "refresco": 1,
                                                  "tostada_especial": 1}),

        Pedido(id= 4, cliente= "Majo", orden = {"chalupa": 15,
                                                "agua": 1,
                                                "pozole": 2})
        ]

@router.get("/")
async def pedido():
    return fk_db

# METODO PARA OBTENER PEDIDO POR ID 
@router.get("/{id}")
async def pedido_id(id: int):
    for index, save_pedido in enumerate(fk_db):
        if save_pedido.id == id:
            return fk_db[index]
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                        detail= "pedido no encontrado")

#METODO PARA AÑADIR PEDIDO    
@router.post("/")
async def add_pedido(pedido: Pedido):
    if type(search_pedido(pedido.id)) == Pedido:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail= "Usuario ya existente")
    fk_db.append(pedido)
    return pedido 

#METODO PARA ACTUALIZAR PEDIDO 
@router.put("/")
async def update_pedido(pedido: Pedido):
    for index, saved_pedido in enumerate(fk_db):
        if saved_pedido.id == pedido.id:
            fk_db[index] = pedido
            return pedido
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                        detail= "Pedido no encontrado")

#METODO PARA BORRAR PEDIDO
@router.delete("/{id}")
async def del_pedido(id: int):
    for index, saved_pedido in enumerate(fk_db):
        if saved_pedido.id == id:
            del fk_db[index]
            return {"message": "Pedido eliminado conééxito"}
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                        detail= "Pedido no encontrado")


def search_pedido(id: int):
    pedidos = filter(lambda pedido: pedido.id == id, fk_db)
    try:
        return list(pedidos)[0]
    except:
        return {"error", "Pedido no encontrado"}

