from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from schemas.user import User
from database.actions_with_user import authentificate_user, get_user_id
from tokens.current_user import get_current_user
from tokens.token_creation import create_access_token

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='',
    tags=['Login']
)

@router.get('/login')
async def return_login_html(request: Request):
    if await get_current_user(request) is None:
        return templates.TemplateResponse("login.html", {"request": request})
    return RedirectResponse(url='/home', status_code=302)

@router.post('/login')
async def login(requset: Request,
                user: User = Form()):
    username = await authentificate_user(user)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    user_id = await get_user_id(username)
    access_token = await create_access_token(username, str(user_id))
    response = RedirectResponse(url='/home', status_code=302)
    response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return response

@router.post('/logout')
async def logout(request: Request):
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie(key='access_token')
    return response
    