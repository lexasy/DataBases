from fastapi import APIRouter, Request 
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from tokens.current_user import get_current_user

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='',
    tags=['Home']
)

@router.get('/home')
async def return_home_html(request: Request):
    if await get_current_user(request) is None:
        return RedirectResponse(url='/login')
    return templates.TemplateResponse("home.html", {"request": request})

