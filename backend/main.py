from fastapi import FastAPI
from routers import pago, pedido, menu

app = FastAPI()

#Routers
app.include_router(pago.router)
app.include_router(pedido.router)
app.include_router(menu.router)

@app.get("/")
async def home(): 
    return "Welcome to Antojitos Mexicanos Kari"
