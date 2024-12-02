from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from tokens.current_user import get_current_user

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

@router.get("/{appliance_id}")
async def get_product_html(request: Request, appliance_id: int):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/login')
    return appliance_id
