from aiogram import Bot, Router, types
from aiogram.filters import Text
from keyboards.inline import get_order_keyboard
from magic_filter import F


router: Router = Router()

menu: dict = {
    "meals": ["meal 1", "meal 2", "meal 3"],
    "drinks": ["drink 1", "drink 2", "drink 3"],
    "desserts": ["dessert 1", "dessert 2", "dessert 3"],
}
orders: dict = {}


@router.callback_query(text="order")
async def orderstart(message: types.Message) -> types.Message:
    return await message.answer(
        "Your cart is empty. Please select your first item:",
        reply_markup=get_order_keyboard(),
    )


# TODO: dynamic inline query
@router.inline_query()
async def menu(inline_query: types.InlineQuery) -> bool:
    # NOTE: to collect the chosen results enable chosen_inline_result
    # via BotFather
    #  @ https://core.telegram.org/bots/inline#collecting-feedback

    # inline_query.answer expects results to be a list of ResuInlineQueryResult

    results: list[types.InlineQueryResult] = [
        types.InlineQueryResultArticle(
            type="article",
            id=item,
            title=f"{item}",
            input_message_content=types.InputTextMessageContent(
                message_text=f"{item} has been added to the cart",
                parse_mode="HTML",
            ),
        )
        for item in ("item 1", "item 2", "item 3")
    ]
    # CallbackQuery must be answered
    # with a call to the asnwerCallbackQuery method
    # https://core.telegram.org/bots/api#callbackquery
    return await inline_query.answer(results, is_personal=True)


@router.chosen_inline_result()
async def add_to_cart(
    chosen_inline_result: types.ChosenInlineResult, bot: Bot
):
    # return bot.send_message(chosen_inline_result.result_id)
    pass
