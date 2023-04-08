from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton


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
        KeyboardButton(text="Add discord"),
        KeyboardButton(text="Add twitter"),
        KeyboardButton(text="Edit discord"),
        KeyboardButton(text="Delete discord"),
        KeyboardButton(text="Delete twitter"),
        KeyboardButton(text="Edit twitter"),
        KeyboardButton(text="Get data"),
        KeyboardButton(text="Export"),
        KeyboardButton(text="BTC"),
        KeyboardButton(text="Sellers")
    ]
    start_keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        input_field_placeholder="Choose action",
        row_width=3
    )
    start_keyboard.row(KeyboardButton(text="Add discord"),
                       KeyboardButton(text="Edit discord"),
                       KeyboardButton(text="Delete discord"))
    start_keyboard.row(KeyboardButton(text="Add twitter"),
                       KeyboardButton(text="Edit twitter"),
                       KeyboardButton(text="Delete twitter"))
    start_keyboard.row(KeyboardButton(text="Get data"),
                       KeyboardButton(text="Export"),
                       KeyboardButton(text="BTC"),
                       KeyboardButton(text="Sellers"))
    return start_keyboard


columns = ReplyKeyboardMarkup(
    resize_keyboard=True,
    input_field_placeholder="Choose column",
).add(KeyboardButton(text="nickname")).add(KeyboardButton(text="login")).add(KeyboardButton(text="password"))

columns1 = ReplyKeyboardMarkup(
    resize_keyboard=True,
    input_field_placeholder="Choose column"
).add(KeyboardButton(text="nickname")).add(KeyboardButton(text="login")).add(KeyboardButton(text="password")).add(
    KeyboardButton(text="phone"))
