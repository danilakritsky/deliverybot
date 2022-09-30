# https://stackoverflow.com/questions/8899198/module-has-no-attribute
# https://stackoverflow.com/questions/35727134/module-imports-and-init-py
from deliverybot.bot.routers import (  # noqa: F401
    cart_router,
    info_router,
    menu_router,
)
