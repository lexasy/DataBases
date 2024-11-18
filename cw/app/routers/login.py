from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from schemas.user import User
from database.actions_with_user import authentificate_user

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='',
    tags=['Login']
)

@router.get('/login')
async def return_login_html(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post('/login')
async def login(requset: Request,
                user: User = Form()):
    username = await authentificate_user(user)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return RedirectResponse(url='/home', status_code=302)