import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from routers import registration, login, home
from database.table_creation import tables_create

app = FastAPI()

app.include_router(registration.router)
app.include_router(login.router)
app.include_router(home.router)

# asyncio.run(tables_create())

@app.get("/")
async def main(request: Request):
    await tables_create()
    return RedirectResponse(url='/login')
