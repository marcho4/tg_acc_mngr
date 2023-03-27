from data.CONFIG import TOKEN
from data import db_session
from data.account import Account
from data.keyboard_maker import empty_keyboard, keyboard, get_start_keyboard
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import StatesGroup, State
from data.crypto_price import get_btc_price
from data.twitter import Twitter

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
tg_uid = 0
curr_nick = curr_login = curr_password = curr_token = ''
db_sess = None
list_of_accs = []


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


class AddingTwtAccount(StatesGroup):
    entering_data = State()
    wrong_data = State()
    accepting = State()


class EditingAcc(StatesGroup):
    choosing_account = State()
    choosing_param = State()
    entering_changes = State()
    accepting_changes = State()


# ------------------------- Cancel Command | Done----------------------------------
@dp.message_handler(commands=['cancel'], state=Global.waiting_for_action)
async def edit_account(message: types.Message):
    await message.answer('There is no command to cancel', reply_markup=empty_keyboard)


@dp.message_handler(commands=['cancel'], state='*')
async def edit_account(message: types.Message):
    await Global.waiting_for_action.set()
    await message.answer('Action canceled', reply_markup=empty_keyboard)


# ------------------------- Start Command | Done----------------------------------
@dp.message_handler(commands=['start'], state=Global.waiting_for_action)
async def already_started(message: types.Message):
    await message.answer('bot has already been started', reply_markup=get_start_keyboard())


@dp.message_handler(commands=['start'], state='*')
async def start_handler(message: types.Message):
    global tg_uid, db_sess
    uid = message.from_user.id
    tg_uid = uid
    db_session.global_init(f"db/{uid}.db")
    db_sess = db_session.create_session()
    await message.answer('Chose one of the commands below', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


# ------------------------- Help Command | Done----------------------------------
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


# ------------------------- Adding Discord | Done----------------------------------
@dp.message_handler(commands=['add_discord'], state=Global.waiting_for_action)
async def add_discord(message: types.Message):
    await AddingAccount.entering_data.set()
    await message.answer(f'enter account data in this format:\n'
                         f' \nnickname;login;password;token\n', reply_markup=empty_keyboard)


# For correct data
@dp.message_handler(lambda message: ';' in message.text and len(message.text.split(';')) == 4 and \
                                    message.text.split(';')[3][:2] == 'OT',
                    state=AddingAccount.entering_data)
async def corr_data(message: types.Message):
    global curr_nick, curr_login, curr_password, curr_token
    curr_nick, curr_login, curr_password, curr_token = message.text.split(';')
    acc = Account()
    acc.user_id = tg_uid
    acc.token = curr_token
    acc.login = curr_login
    acc.nickname = curr_nick
    acc.password = curr_password
    db_sess.add(acc)
    db_sess.commit()
    await message.answer(f'Data accepted')
    await Global.waiting_for_action.set()


# For wrong data
@dp.message_handler(lambda message: ';' not in message.text or len(message.text.split(';')) != 4 and \
                                    message.text.split(';')[3][:2] != 'OT',
                    state=AddingAccount.entering_data)
async def wrong_data(message: types.Message):
    await message.answer('Wrong data, please enter again.\n\n'
                         'If you dont wanna add an account - use /cancel')


# ------------------------- Adding Twitter | Not Ready ----------------------------------
@dp.message_handler(commands=['add_twitter'], state=Global.waiting_for_action)
async def add_twitter(message: types.Message):
    await AddingTwtAccount.entering_data.set()
    await message.answer(f'enter account data in this format:\n'
                         f' \nlogin;password;username;phone', reply_markup=empty_keyboard)


@dp.message_handler(lambda message: ';' in message.text and len(message.text.split(';')) == 4,
                    state=AddingTwtAccount.entering_data)
async def cor_data(message: types.Message):
    acc = Twitter()
    acc.login = message.text.split(';')[0]
    acc.password = message.text.split(';')[1]
    acc.username = message.text.split(';')[2]
    acc.phone = message.text.split(';')[3]
    db_sess.add(acc)
    db_sess.commit()
    await message.answer(f'Data accepted')
    await Global.waiting_for_action.set()


# ------------------------- Editing Account Data | Not Ready ----------------------------------
@dp.message_handler(commands=['edit_account'])
async def edit_account(message: types.Message):
    await message.answer(f'chose account')
    await AddingTwtAccount.entering_data.set()


# ------------------------- Get Data Command | Done----------------------------------
@dp.message_handler(commands=['get_data'], state=Global.waiting_for_action)
async def get_data(message: types.Message):
    global list_of_accs, db_sess
    list_of_accs = []
    db_sess = db_session.create_session()
    kb = [[]]
    for acc in db_sess.query(Account).filter(Account.user_id == tg_uid):
        kb[0].append(types.KeyboardButton(text=str(acc.nickname)))
        list_of_accs.append(str(acc.nickname))
    list_of_accounts = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="chose account"
    )
    await message.answer(f'chose account', reply_markup=list_of_accounts)
    await GettingData.choosing_account.set()


@dp.message_handler(lambda message: message.text in list_of_accs, state=GettingData.choosing_account)
async def send_data(message: types.Message):
    global db_sess
    db_sess = db_session.create_session()
    account = db_sess.query(Account).filter(Account.nickname == message.text).first()
    await message.answer(account.get_acc_data(), reply_markup=empty_keyboard)
    await Global.waiting_for_action.set()


@dp.message_handler(lambda message: message.text not in list_of_accs, state=GettingData.choosing_account)
async def wrong_acc(message: types.Message):
    await message.answer("There isn't any accounts with this nickname\n\nTo cancel use /cancel")


# ------------------------- Simple Commands Just For Fun ----------------------------------
@dp.message_handler(commands=['sigma'], state=Global.waiting_for_action)
async def sigma(message: types.Message):
    await message.answer(f'https://youtube.com/shorts/NrIQMPwUyTg?feature=share')


@dp.message_handler(commands=['btc'], state=Global.waiting_for_action)
async def btc(message: types.Message):
    await message.answer(get_btc_price())


# async def acceptation(msg: types.Message):
#     await msg.answer('Do you submit your data?', reply_markup=kb1)


if __name__ == '__main__':
    executor.start_polling(dp)
