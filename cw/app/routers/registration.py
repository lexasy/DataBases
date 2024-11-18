from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from schemas.user import User
from database.actions_with_user import get_user, create_user


templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='',
    tags=['Registration']
)

@router.get("/register")
async def return_registration_html(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(requset: Request,
                       user: User = Form()):
    existing_user = await get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    await create_user(user)
    return RedirectResponse(url='/home', status_code=302)
    

