from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import accountsControllers, authControllers, customersControllers, transactionsControllers

app = FastAPI(title="BankAppDW API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authControllers.router)
app.include_router(customersControllers.router)
app.include_router(accountsControllers.router)
app.include_router(transactionsControllers.router)
