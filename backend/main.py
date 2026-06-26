from fastapi import FastAPI
from routers import pago, pedido

app = FastAPI()

#Routers
app.include_router(pago.router)
app.include_router((pedido.router))

@app.get("/")
async def home(): 
    return "Welcome to Antojitos Mexicanos Kari"
