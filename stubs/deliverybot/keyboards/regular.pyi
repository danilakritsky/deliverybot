from aiogram import types


BUTTONS: list[types.KeyboardButton]
PLACEHOLDER: str

def get_single_row_keyboard(
    buttons: list[types.KeyboardButton] = ...,
    resize_keyboard: bool = ...,
    input_field_placeholder: str = ...,
) -> types.ReplyKeyboardMarkup: ...
def get_initial_keyboard() -> types.ReplyKeyboardMarkup: ...
def get_post_about_keyboard() -> types.ReplyKeyboardMarkup: ...
