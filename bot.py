from data.CONFIG import TOKEN
from data import db_session
from data.account import Account
from data.keyboard_maker import empty_keyboard, make_row_keyboard
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import StatesGroup, State
from data.crypto_price import get_btc_price

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
add_ds = add_tw = started = False
tg_uid = 0
curr_nick = curr_login = curr_pswrd = curr_token = ''
db_sess = None


class Global(StatesGroup):
    not_started = State()
    waiting_for_action = State()


class GettingData(StatesGroup):
    choosing_account = State()
    accepting = State()


class AddingAccount(StatesGroup):
    entering_data = State()
    wrong_data = State()
    accepting = State()


# fun commands
@dp.message_handler(commands=['sigma'], state='*')
async def sigma(message: types.Message):
    await message.answer(f'https://youtube.com/shorts/NrIQMPwUyTg?feature=share')


@dp.message_handler(commands=['btc'], state='*')
async def btc(message: types.Message):
    await message.answer(get_btc_price())


@dp.message_handler(commands=['start'], state='*')
async def start_handler(message: types.Message):
    global tg_uid, started, db_sess
    first_name = message.from_user.full_name
    uid = message.from_user.id
    tg_uid = uid
    db_session.global_init(f"db/{uid}.db")
    db_sess = db_session.create_session()
    kb = [
        [
            types.KeyboardButton(text="/add_discord"),
            types.KeyboardButton(text="/add_twitter"),
            types.KeyboardButton(text="/edit_account"),
            types.KeyboardButton(text="/get_data")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="chose action"
    )
    await message.answer(f'GM, {first_name}')
    await message.answer('Chose one of the commands below', reply_markup=keyboard)
    await Global.waiting_for_action.set()
    # await message.answer('You have already started the bot')


@dp.message_handler(state='*', commands=['help'])
async def help_handler(message: types.Message):
    await message.answer(f'/start\n'
                         f'/help - list of all available commands\n'
                         f'/add_discord - add discord account to the data base\n'
                         f'/add_twitter - add twitter account to the data base\n'
                         f'/edit_account - edit data for the chosen account\n'
                         f'/get_data - get data of the account\n'
                         f'/cancel - cancel the command\n'
                         f'/sigma - sigma rules for real men\n'
                         f'/btc - current price of BTC')


# Adding discord to the database
@dp.message_handler(commands=['add_discord'], state=Global.waiting_for_action)
async def add_discord(message: types.Message):
    await AddingAccount.entering_data.set()
    await message.answer(f'enter account data in this format:\n'
                         f' \nnickname;login;password;token\n', reply_markup=empty_keyboard)


@dp.message_handler(lambda message: ';' in message.text and len(message.text.split(';')) == 4 and \
                                    message.text.split(';')[3][:2] == 'OT',
                    state=AddingAccount.entering_data)
async def corr_data(message: types.Message):
    global curr_nick, curr_login, curr_pswrd, curr_token
    curr_nick, curr_login, curr_pswrd, curr_token = message.text.split(';')
    acc = Account()
    acc.user_id = tg_uid
    acc.token = curr_token
    acc.login = curr_login
    acc.nickname = curr_nick
    acc.password = curr_pswrd
    db_sess.add(acc)
    db_sess.commit()
    await message.answer(f'Data accepted')
    await Global.waiting_for_action.set()


@dp.message_handler(lambda message: ';' not in message.text or len(message.text.split(';')) != 4 and \
                                    message.text.split(';')[3][:2] != 'OT',
                    state=AddingAccount.entering_data)
async def wrong_data(message: types.Message):
    await message.answer('Wrong data, please enter again')


@dp.message_handler(commands=['add_twitter'])
async def add_twitter(message: types.Message):
    await message.answer(f'chose account')


@dp.message_handler(commands=['edit_account'])
async def edit_account(message: types.Message):
    await message.answer(f'chose account')


@dp.message_handler(commands=['cancel'], state='')
async def edit_account(message: types.Message):
    await Global.waiting_for_action.set()
    await message.answer('Action canceled', reply_markup=empty_keyboard)
    await message.answer('There is no command to cancel', reply_markup=empty_keyboard)
    await Global.waiting_for_action.set()


@dp.message_handler(commands=['get_data'], state=Global.waiting_for_action)
async def get_data(message: types.Message):
    db_sess = db_session.create_session()
    kb = [[]]
    for acc in db_sess.query(Account).filter(Account.user_id == tg_uid):
        kb[0].append(types.KeyboardButton(text=str(acc.nickname)))
    print(kb)
    list_of_accounts = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="chose account"
    )
    await message.answer(f'chose account', reply_markup=list_of_accounts)
    await GettingData.choosing_account.set()


@dp.message_handler()
async def msg(message: types.Message):
    global add_ds, curr_nick, curr_login, curr_pswrd, curr_token, db_sess
    while add_ds:
        if ';' in message.text and len(message.text.split(';')) == 4:
            curr_nick, curr_login, curr_pswrd, curr_token = message.text.split(';')
            print(curr_token[:2])
            if curr_token[:2] != 'OT':
                await message.answer('You entered token in wrong format')
                add_ds = False
            else:
                # state = 'waiting_for_acception'
                acc = Account()
                acc.user_id = tg_uid
                acc.token = curr_token
                acc.login = curr_login
                acc.nickname = curr_nick
                acc.password = curr_pswrd
                db_sess.add(acc)
                db_sess.commit()
                await message.answer(f'Data accepted')
            # async def acception(msg: types.Message):
            #     kb1 = [
            #         [types.KeyboardButton(text='Yes'),
            #          types.KeyboardButton(text='No')],
            #     ]
            #     keyb = types.ReplyKeyboardMarkup(
            #         keyboard=kb1,
            #         resize_keyboard=True,
            #         input_field_placeholder="Do you submit your data?"
            #     )
            #     await msg.answer('Do you submit your data?', reply_markup=keyb)
            # @dp.message_handler()
            # async def accept(message: types.Message):
            #     if
            add_ds = False
        else:
            await message.answer('You entered data in wrong format')
            add_ds = False


if __name__ == '__main__':
    executor.start_polling(dp)
