from fastapi                import FastAPI, Depends, HTTPException, Security, status,Response,Header
from fastapi.responses      import JSONResponse
from fastapi.security       import HTTPBearer, HTTPAuthorizationCredentials
from dotenv                 import load_dotenv
from pydantic               import BaseModel
from datetime               import datetime
from models.transaction     import Transaction

import pandas                as pd
import uvicorn
import asyncio

app = FastAPI(
    title="Api v1 de Transaction",
    description="Criando uma APi bancária de transações, exercicio da Formação Back-End python da Dio.me"
)

@app.get("/")
async def ping():
    return JSONResponse(
        content={
            "message": "Conected",
            "statys":"200"
        }
    ) 

@app.get("/ping")
async def ping():
    return JSONResponse(
        content={
            "message": "Pong"
        }
    ) 



#------------------------TRANSACTIONS---------------------------------------










if __name__ == "__main__":
    uvicorn.run("Api.app:app", port=3000, reload=True)
