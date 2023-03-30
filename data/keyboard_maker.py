from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


empty_keyboard = ReplyKeyboardRemove()

kb1 = [
    [KeyboardButton(text='Yes'),
     KeyboardButton(text='No')],
]
keyboard = ReplyKeyboardMarkup(
    keyboard=kb1,
    resize_keyboard=True,
    input_field_placeholder="Do you submit your data?"
)


def get_start_keyboard():
    commands = [
        [
            KeyboardButton(text="/add_discord"),
            KeyboardButton(text="/add_twitter"),
            KeyboardButton(text="/edit_account"),
            KeyboardButton(text="/get_data"),
            KeyboardButton(text="/btc"),
            KeyboardButton(text="/sigma")
        ],
    ]
    start_keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        input_field_placeholder="chose action"
    )
    for x in commands[0]:
        start_keyboard.add(x)
    return start_keyboard


columns = ReplyKeyboardMarkup(
    resize_keyboard=True,
    input_field_placeholder="Choose column"
).add(KeyboardButton(text="nickname")).add(KeyboardButton(text="login")).add(KeyboardButton(text="password"))
