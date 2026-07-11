from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def game_reply_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="My Info"),
                KeyboardButton(text="My Bets"),
                KeyboardButton(text="လောင်းခြင်းပယ်ဖျက်")
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return kb

def result_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 My Info", callback_data="my_info_inline")]
        ]
    )
    return kb
