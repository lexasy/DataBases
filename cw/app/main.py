import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from routers import registration, login, home, products, basket

app = FastAPI()

app.include_router(registration.router)
app.include_router(login.router)
app.include_router(home.router)
app.include_router(products.router)
app.include_router(basket.router)


@app.get("/")
async def main(request: Request):
    return RedirectResponse(url='/login')
