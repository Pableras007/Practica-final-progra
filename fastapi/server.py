import shutil
import io
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form
import pandas as pd
from typing import List
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class RugbyMatch(BaseModel):
    date: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    competition: str
    stadium: str
    city: str
    country: str
    neutral: bool
    world_cup: bool


class ListadoPartidos(BaseModel):
    partidos = List[RugbyMatch]


app = FastAPI(
    title="Servidor de datos",
    description="""Servimos datos de partidos de rugby""",
    version="0.1.0",
)


@app.get("/retrieve_data/")
def retrieve_data():
    todosmisdatos = pd.read_csv('results.csv', sep=',')
    todosmisdatos = todosmisdatos.fillna(0)
    todosmisdatosdict = todosmisdatos.to_dict(orient='records')
    listado = ListadoPartidos()
    listado.partidos = todosmisdatosdict
    return listado
