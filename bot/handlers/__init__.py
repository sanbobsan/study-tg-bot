from aiogram import Router

from .admin import router as admin_router
from .easter_eggs import router as easter_router
from .menu import router as menu_router
from .register import router as register_router
from .start import router as start_router

main_router = Router()
main_router.include_routers(
    start_router,
    register_router,
    menu_router,
    admin_router,
    easter_router,
)


__all__ = [
    "main_router",
]
