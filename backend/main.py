from fastapi import FastAPI
from app.api.routers import auth, accidente
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000",  # React
    "http://127.0.0.1:3000",
    'http://localhost:5173',
    'http://localhost:8000',
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://192.168.1.100:8000",
    "http://192.168.137.122:8000",
    "http://192.168.79.63:8000", 

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(accidente.router)


@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}