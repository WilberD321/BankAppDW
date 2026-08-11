from __future__ import annotations

from fastapi import FastAPI

from app.controllers import accountsControllers, customersControllers, transactionsControllers

app = FastAPI(title="BankAppDW API")

app.include_router(customersControllers.router)
app.include_router(accountsControllers.router)
app.include_router(transactionsControllers.router)
