from fastapi import FastAPI
from routers import pago,menu,orden

app = FastAPI()

#Routers
app.include_router(pago.router)
app.include_router(menu.router)
app.include_router(orden.router)

@app.get("/")
async def home(): 
    return "Welcome to Antojitos Mexicanos Kari"
