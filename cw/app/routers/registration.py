from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from schemas.user import User
from database.actions_with_user import get_user, create_user, get_user_id
from tokens.current_user import get_current_user
from tokens.token_creation import create_access_token


templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='',
    tags=['Registration']
)

@router.get("/register")
async def return_registration_html(request: Request):
    if await get_current_user(request) is None:
        return templates.TemplateResponse("register.html", {"request": request})
    return RedirectResponse(url='/home', status_code=302)

@router.post("/register")
async def register(requset: Request,
                       user: User = Form()):
    existing_user = await get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    await create_user(user)
    user_id = await get_user_id(user.username)
    access_token = await create_access_token(user.username, str(user_id))
    response = RedirectResponse(url='/home', status_code=302)
    response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return response
    

