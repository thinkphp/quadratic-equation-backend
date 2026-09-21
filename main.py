"""
Backend FastAPI pentru rezolvarea ecuatiei de gradul 2: ax^2 + bx + c = 0

Ruleaza cu: uvicorn main:app --reload --port 8000
"""

import math
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Rezolvator ecuatie de gradul 2")

# Permite cereri doar de la frontend-ul React (Vite implicit pe 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class Coeficienti(BaseModel):
    a: float
    b: float
    c: float


class Radacina(BaseModel):
    real: float
    imaginar: float = 0.0


class Rezultat(BaseModel):
    tip: str              # "doua_reale" | "reala_dubla" | "complexe" | "liniara"
    discriminant: float | None = None
    radacini: list[Radacina]


@app.post("/solve", response_model=Rezultat)
def solve(coef: Coeficienti):
    a, b, c = coef.a, coef.b, coef.c

    # Cazul degenerat: nu e ecuatie de gradul 2, ci liniara (bx + c = 0)
    if a == 0:
        if b == 0:
            raise HTTPException(
                status_code=400,
                detail="a si b nu pot fi ambele 0 -- nu exista ecuatie de rezolvat.",
            )
        x = -c / b
        return Rezultat(tip="liniara", radacini=[Radacina(real=x)])

    discriminant = b * b - 4 * a * c

    if discriminant > 0:
        radical = math.sqrt(discriminant)
        x1 = (-b + radical) / (2 * a)
        x2 = (-b - radical) / (2 * a)
        return Rezultat(
            tip="doua_reale",
            discriminant=discriminant,
            radacini=[Radacina(real=x1), Radacina(real=x2)],
        )

    if discriminant == 0:
        x = -b / (2 * a)
        return Rezultat(
            tip="reala_dubla",
            discriminant=discriminant,
            radacini=[Radacina(real=x)],
        )

    # discriminant < 0 -> radacini complexe conjugate
    parte_reala = -b / (2 * a)
    parte_imaginara = math.sqrt(-discriminant) / (2 * a)
    return Rezultat(
        tip="complexe",
        discriminant=discriminant,
        radacini=[
            Radacina(real=parte_reala, imaginar=parte_imaginara),
            Radacina(real=parte_reala, imaginar=-parte_imaginara),
        ],
    )


@app.get("/health")
def health():
    return {"status": "ok"}
