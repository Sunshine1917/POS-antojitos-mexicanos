from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def home(): 
    return "Welcome to Antojitos Mexicanos Kari"
