from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from data.CONFIG import TOKEN
from data.account import Account
from data.keyboard_maker import empty_keyboard, get_start_keyboard, columns, columns1
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from data.crypto_price import get_btc_price
from data.twitter import Twitter
from data.states import Global, GettingData, AddingTwtAccount, EditingAcc, BulkAdd, DeleteDiscord, DeleteTwitter, \
    EditingTwitter
from data.get_session import get_session

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
curr_nick = curr_login = curr_password = curr_token = ''
twt_phone = twt_username = twt_password = twt_login = ''
list_of_accounts = []
list_of_twt = []
chosen_account = ''


# ------------------------- Cancel Command ----------------------------------
@dp.message_handler(commands=['cancel'], state=Global.waiting_for_action)
async def edit_account(message: types.Message):
    await message.answer('There is no command to cancel', reply_markup=get_start_keyboard())


@dp.message_handler(commands=['cancel'], state='*')
async def edit_account(message: types.Message):
    await Global.waiting_for_action.set()
    await message.answer('Action canceled', reply_markup=get_start_keyboard())


# ------------------------- Start Command -----------------------------------
@dp.message_handler(commands=['start'], state=Global.waiting_for_action)
async def already_started(message: types.Message):
    await message.answer('bot has already been started', reply_markup=get_start_keyboard())


@dp.message_handler(commands=['start'], state='*')
async def start_handler(message: types.Message):
    await message.answer('Chose one of the commands below', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


# ------------------------- Help Command -----------------------------------
@dp.message_handler(lambda msg: msg.text.lower() == 'help', state='*')
async def help_handler(message: types.Message):
    await message.answer(
        f'Help - list of all available commands\n'
        f'Add discord - add discord account to the data base\n'
        f'Add twitter - add twitter account to the data base\n'
        f'Delete discord - delete discord account from the data base\n'
        f'Delete twitter - delete twitter account from the data base\n'
        f'Edit discord - edit data for the chosen discord\n'
        f'Edit twitter - edit data for the chosen discord\n'
        f'Get data - get data of the account\n'
        f'/cancel - cancel any command\n'
        f'Sellers - get best account sellers\n'
        f'BTC - current price of BTC')


# ------------------------- Adding Twitter ----------------------------------
@dp.message_handler(lambda msg: msg.text == 'Add twitter', state=Global.waiting_for_action)
async def add_twitter(message: types.Message):
    await AddingTwtAccount.entering_data.set()
    await message.answer(f'Enter account data in this format:\n'
                         f' \nlogin:password:username:phone\n\nTo cancel use /cancel', reply_markup=empty_keyboard)


@dp.message_handler(lambda message: ':' in message.text and len(message.text.split(':')) == 4,
                    state=AddingTwtAccount.entering_data)
async def cor_data(message: types.Message):
    global twt_phone, twt_username, twt_password, twt_login, list_of_accounts
    twt_login, twt_password, twt_username, twt_phone = message.text.split(':')
    list_of_accounts = []
    session = get_session()
    kb = types.ReplyKeyboardMarkup(input_field_placeholder="Select account")
    for acc in session.query(Account).filter(Account.user_id == message.from_user.id):
        kb.add(types.KeyboardButton(text=str(acc.nickname)))
        list_of_accounts.append(str(acc.nickname))
    await message.answer(f'Select the account to which you want to link this data', reply_markup=kb)
    await AddingTwtAccount.choosing_discord.set()


@dp.message_handler(lambda message: message.text in list_of_accounts,
                    state=AddingTwtAccount.choosing_discord)
async def wd(message: types.Message):
    twt = Twitter()
    twt.login, twt.username, twt.discord_nickname, twt.password, twt.phone, twt.user_id = twt_login, twt_username, str(
        message.text), twt_password, twt_phone, message.from_user.id
    session = get_session()
    session.add(twt)
    session.commit()
    await message.answer('Data accepted.', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


@dp.message_handler(lambda message: message.text not in list_of_accounts,
                    state=AddingTwtAccount.choosing_discord)
async def wd(message: types.Message):
    await message.answer('There is no discord account with this name.\n\n'
                         'Please, choose one from the list below.\n\nTo cancel use /cancel')


@dp.message_handler(lambda message: ';' not in message.text or len(message.text.split(';')) != 4,
                    state=AddingTwtAccount.entering_data)
async def wd(message: types.Message):
    await message.answer('Wrong data or format, please enter again.\n\n'
                         'If you dont wanna add an account - use /cancel')


# ------------------------- Editing Account Data ----------------------------------
@dp.message_handler(lambda msg: msg.text == 'Edit discord', state=Global.waiting_for_action)
async def edit_account(message: types.Message):
    global list_of_accounts
    list_of_accounts = []
    session = get_session()
    kb = ReplyKeyboardMarkup(row_width=3, input_field_placeholder="Select account")
    for acc in session.query(Account).filter(Account.user_id == message.from_user.id):
        kb.insert(types.KeyboardButton(text=str(acc.nickname)))
        list_of_accounts.append(str(acc.nickname))
    await message.answer(f'Choose account\n\nTo cancel use /cancel', reply_markup=kb)
    await EditingAcc.choosing_account.set()


@dp.message_handler(lambda message: message.text in list_of_accounts, state=EditingAcc.choosing_account)
async def choosing_column(message: types.Message):
    global chosen_account
    chosen_account = message.text
    await message.answer('Choose parameter to edit', reply_markup=columns)
    await EditingAcc.choosing_param.set()


@dp.message_handler(lambda message: message.text in ['nickname', 'password', 'login'], state=EditingAcc.choosing_param)
async def choosing_param(message: types.Message):
    if message.text == 'nickname':
        await message.answer('Enter new value', reply_markup=empty_keyboard)
        await EditingAcc.nickname.set()
    if message.text == 'login':
        await message.answer('Enter new value', reply_markup=empty_keyboard)
        await EditingAcc.login.set()
    if message.text == 'password':
        await message.answer('Enter new value', reply_markup=empty_keyboard)
        await EditingAcc.password.set()


@dp.message_handler(state=EditingAcc.password)
async def wait(message: types.Message):
    session = get_session()
    acc = session.query(Account).filter(Account.nickname == chosen_account).first()
    acc.password = message.text
    session.commit()
    await message.answer(f'New password was set', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


@dp.message_handler(state=EditingAcc.login)
async def wait(message: types.Message):
    session = get_session()
    acc = session.query(Account).filter(Account.nickname == chosen_account).first()
    acc.login = message.text
    session.commit()
    await message.answer(f'New login was set', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


@dp.message_handler(state=EditingAcc.nickname)
async def wait(message: types.Message):
    session = get_session()
    acc = session.query(Account).filter(Account.nickname == chosen_account).first()
    acc.nickname = message.text
    session.commit()
    await message.answer(f'New nickname was set', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


@dp.message_handler(lambda message: message.text not in list_of_accounts, state=EditingAcc.choosing_account)
async def wait(message: types.Message):
    await message.answer('There is no account with this nickname')


# -------------- Editing Twitter --------------------
@dp.message_handler(lambda msg: msg.text == 'Edit twitter', state=Global.waiting_for_action)
async def edit_twitter(message: types.Message):
    global list_of_twt
    list_of_twt = []
    session = get_session()
    kb = ReplyKeyboardMarkup(row_width=3, input_field_placeholder="Select account")
    for acc in session.query(Twitter).filter(Twitter.user_id == message.from_user.id):
        kb.insert(types.KeyboardButton(text=str(acc.username)))
        list_of_twt.append(str(acc.username))
    await message.answer(f'Select the account\n\nTo cancel use /cancel', reply_markup=kb)
    await EditingTwitter.choosing_account.set()


@dp.message_handler(lambda message: message.text in list_of_twt, state=EditingTwitter.choosing_account)
async def choosing_column(message: types.Message):
    global chosen_account
    chosen_account = message.text
    await message.answer('Choose parameter to edit', reply_markup=columns1)
    await EditingTwitter.choosing_param.set()


@dp.message_handler(lambda message: message.text in ['nickname', 'password', 'login', 'phone'],
                    state=EditingTwitter.choosing_param)
async def choosing_param(message: types.Message):
    if message.text == 'nickname':
        await message.answer('Enter new value', reply_markup=empty_keyboard)
        await EditingTwitter.nickname.set()
    if message.text == 'login':
        await message.answer('Enter new value', reply_markup=empty_keyboard)
        await EditingTwitter.login.set()
    if message.text == 'password':
        await message.answer('Enter new value', reply_markup=empty_keyboard)
        await EditingTwitter.password.set()
    if message.text == 'phone':
        await message.answer('Enter new value', reply_markup=empty_keyboard)
        await EditingTwitter.phone.set()


@dp.message_handler(state=EditingTwitter.password)
async def wait(message: types.Message):
    session = get_session()
    acc = session.query(Twitter).filter(Twitter.username == chosen_account).first()
    acc.password = message.text
    session.commit()
    await message.answer(f'New password was set', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


@dp.message_handler(state=EditingTwitter.login)
async def wait(message: types.Message):
    session = get_session()
    acc = session.query(Twitter).filter(Twitter.username == chosen_account).first()
    acc.login = message.text
    session.commit()
    await message.answer(f'New login was set', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


@dp.message_handler(state=EditingTwitter.nickname)
async def wait(message: types.Message):
    session = get_session()
    acc = session.query(Twitter).filter(Twitter.username == chosen_account).first()
    acc.username = message.text
    session.commit()
    await message.answer(f'New username was set', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


@dp.message_handler(state=EditingTwitter.phone)
async def phone(message: types.Message):
    session = get_session()
    acc = session.query(Twitter).filter(Twitter.username == chosen_account).first()
    acc.phone = message.text
    session.commit()
    await message.answer(f'New password was set', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


@dp.message_handler(lambda message: message.text not in list_of_accounts, state=EditingAcc.choosing_account)
async def wait(message: types.Message):
    await message.answer('There is no account with this nickname')


# ------------------------- Get Data Command ----------------------------------
@dp.message_handler(lambda msg: msg.text == 'Get data', state=Global.waiting_for_action)
async def get_data(message: types.Message):
    global list_of_accounts
    list_of_accounts = []
    session = get_session()
    kb = ReplyKeyboardMarkup(row_width=3, input_field_placeholder="Select account")
    for acc in session.query(Account).filter(Account.user_id == message.from_user.id):
        kb.insert(KeyboardButton(str(acc.nickname)))
        list_of_accounts.append(str(acc.nickname))
    if list_of_accounts:
        await message.answer(f'Choose account\n\nTo cancel use /cancel', reply_markup=kb)
        await GettingData.choosing_account.set()
    else:
        await message.answer(f'There is no accounts in the database', reply_markup=get_start_keyboard())


@dp.message_handler(lambda message: message.text in list_of_accounts, state=GettingData.choosing_account)
async def send_data(message: types.Message):
    session = get_session()
    account = session.query(Account).filter(Account.nickname == message.text).first()
    twt = session.query(Twitter).filter(Twitter.discord_nickname == message.text).first()
    if account:
        await message.answer(account.get_acc_data(), reply_markup=get_start_keyboard())
    if twt:
        await message.answer(twt.get_acc_data(), reply_markup=get_start_keyboard())
    if not twt and not account:
        await message.answer("There isn't any data", reply_markup=empty_keyboard)
    await Global.waiting_for_action.set()


@dp.message_handler(lambda message: message.text not in list_of_accounts, state=GettingData.choosing_account)
async def wrong_acc(message: types.Message):
    await message.answer("There isn't any accounts with this nickname\n\nTo cancel use /cancel")


# ------------------- Adding Discord ----------------------
@dp.message_handler(lambda msg: msg.text == 'Add discord', state=Global.waiting_for_action)
async def bulk(msg: types.Message):
    await msg.answer(
        'Enter account data in this format:\n\nlogin:password:token:nick\n\nYou can add multiple accounts'
        '\n\nTo cancel use /cancel')
    await BulkAdd.entering.set()


@dp.message_handler(state=BulkAdd.entering)
async def getting_bulk_data(msg: types.Message):
    try:
        session = get_session()
        data = msg.text.split()
        for x in data:
            acc = Account()
            acc.user_id = msg.from_user.id
            acc.login, acc.password, acc.token, acc.nickname = x.split(':')
            session.add(acc)
        session.commit()
        await msg.answer('Accounts accepted', reply_markup=get_start_keyboard())
        await Global.waiting_for_action.set()
    except Exception:
        await msg.answer('Something went wrong\nRestart the command', reply_markup=get_start_keyboard())
        await Global.waiting_for_action.set()


# ---------------------------------------- Delete Discord ------------------------------------
@dp.message_handler(lambda msg: msg.text == 'Delete discord', state=Global.waiting_for_action)
async def delete_choice(message: types.Message):
    global list_of_accounts
    list_of_accounts = []
    session = get_session()
    kb = ReplyKeyboardMarkup(row_width=3, input_field_placeholder="Select account")
    for acc in session.query(Account).filter(Account.user_id == message.from_user.id):
        kb.insert(KeyboardButton(str(acc.nickname)))
        list_of_accounts.append(str(acc.nickname))
    await message.answer(f'Choose account\n\nTo cancel use /cancel', reply_markup=kb)
    await DeleteDiscord.choosing.set()


@dp.message_handler(lambda message: message.text in list_of_accounts, state=DeleteDiscord.choosing)
async def delete_choice(message: types.Message):
    session = get_session()
    session.delete(session.query(Account).filter(Account.nickname == message.text).first())
    session.commit()
    await message.answer('Account has been successfully deleted', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


@dp.message_handler(lambda message: message not in list_of_accounts, state=DeleteDiscord.choosing)
async def error(message: types.Message):
    await message.answer('There is no account with this nickname, please try again', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


# ---------------------------------------- Delete Twitter ------------------------------------
@dp.message_handler(lambda msg: msg.text == 'Delete twitter', state=Global.waiting_for_action)
async def delete_twt_choice(message: types.Message):
    global list_of_twt
    list_of_twt = []
    session = get_session()
    kb = ReplyKeyboardMarkup(row_width=3, input_field_placeholder="Select account")
    for acc in session.query(Twitter).filter(Twitter.user_id == message.from_user.id):
        kb.insert(types.KeyboardButton(text=str(acc.username)))
        list_of_twt.append(str(acc.username))
    await message.answer(f'Choose account\n\nTo cancel use /cancel', reply_markup=kb)
    await DeleteTwitter.choosing.set()


@dp.message_handler(lambda message: message.text in list_of_twt, state=DeleteTwitter.choosing)
async def delete_twt(msg: types.Message):
    session = get_session()
    session.delete(session.query(Twitter).filter(Twitter.username == msg.text).first())
    session.commit()
    await msg.answer('Account has been successfully deleted', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


@dp.message_handler(lambda message: message not in list_of_twt, state=DeleteTwitter.choosing)
async def error_twt(msg: types.Message):
    await msg.answer('There is no twitter with this username, please try again', reply_markup=get_start_keyboard())
    await Global.waiting_for_action.set()


# ------------------------- Simple Commands Just For Fun ----------------------------------
@dp.message_handler(lambda msg: msg.text == 'BTC', state=Global.waiting_for_action)
async def btc(message: types.Message):
    await message.answer(get_btc_price())


@dp.message_handler(lambda msg: msg.text == 'Export', state=Global.waiting_for_action)
async def btc(message: types.Message):
    session = get_session()
    with open('accounts.txt', 'w+') as doc:
        for ds in session.query(Account).filter(Account.user_id == message.from_user.id).all():
            doc.write(f'{ds.login}:{ds.password}:{ds.token}:{ds.nickname}' + '\n')
        doc.write('\nTwitters\n')
        for twt in session.query(Twitter).filter(Twitter.user_id == message.from_user.id).all():
            doc.write(
                f'{twt.login}:{twt.password}:{twt.username}:{twt.phone} connected to {twt.discord_nickname}' + '\n')
        doc.close()
    with open('accounts.txt', 'rb') as f:
        await bot.send_document(message.from_user.id, f)
        f.close()


@dp.message_handler(lambda msg: msg.text == 'Sellers', state=Global.waiting_for_action)
async def sigma(message: types.Message):
    await message.answer(
        f'Discord accounts\n\n'
        f'https://darkstore.biz/products/view/akkaunty-discord-pocta-ramblerru-token-sms-verified-mailpasswordtoken'
        f'-otlezka-1-7-dnej\n\n'
        f'Twitter accounts\n\n'
        f'https://darkstore.biz/products/view/twitter-avatar-polnaa-verifikacia-2022-podtverzdeno-po-sms-podtve'
        f'rzdeno-po-pocte-gmx-parol-pocty-ne-predostavlaetsa-zen-authtoken')


if __name__ == '__main__':
    executor.start_polling(dp)
