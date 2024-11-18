from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='',
    tags=['Home']
)

@router.get('/home')
async def return_home_html(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

