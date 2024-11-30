from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from tokens.current_user import get_current_user
from database.actions_with_products import get_all_products, add_new_product
from database.actions_with_customers import validate_admin, get_all_customers, add_new_admin
from database.actions_with_brands import get_all_brands, add_new_brand
from database.actions_with_categories import get_all_categories, add_new_category
from schemas.appliance import Appliance
from schemas.brand import Brand
from schemas.category import Category
# from database.actions_with_products import insert_new_product

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/home',
    tags=['Home']
)

@router.get('/')
async def return_home_html(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/login')
    products = await get_all_products()
    if await validate_admin(user) == user:
        brands = await get_all_brands()
        categories = await get_all_categories()
        return templates.TemplateResponse("home_admin.html",
                                        {
                                            "request": request,
                                            "brands": brands,
                                            "categories": categories,
                                            "products": products
                                        })
    return templates.TemplateResponse("home.html",
                                    {
                                        "request": request,
                                        "products": products
                                    })

@router.post('/add_appliance')
async def add_new_appliance_query(request: Request,
                                appliance: Appliance = Form()):
    if (len(appliance.description) == 0):
        appliance.description = None
    await add_new_product(appliance)
    return {"message": "Товар был добавлен успешно!"}

@router.post('/add_brand')
async def add_new_brand_query(request: Request,
                            brand: Brand = Form()):
    if (len(brand.description) == 0):
        brand.description = None
    await add_new_brand(brand)
    return {"message": "Бренд был добавлен успешно!"}

@router.post('/add_category')
async def add_new_category_query(request: Request,
                                category: Category = Form()):
    if (len(category.description) == 0):
        category.description = None
    await add_new_category(category)
    return {"message": "Категория была добавлена успешно!"}

@router.get('/add_admin') # протестить рандомный заход по URL
async def all_customers_getter(request: Request):
    customers = await get_all_customers()
    return customers

@router.post('/add_admin')
async def add_new_admin_query(request: Request,
                              username: str = Form()):
    await add_new_admin(username)
    return {"message": "Новый администратор назначен успешно!"}
    
    

# @router.get('/home/add')
# async def return_add_booking_html(request: Request):
#     if await get_current_user(request) is None:
#         return RedirectResponse(url='/login')
#     return templates.TemplateResponse("add.html", {"request": request})

# @router.post('/home/add')
# async def add_booking(request: Request,
#                       product: Product = Form()):
#     await insert_new_product(product)
