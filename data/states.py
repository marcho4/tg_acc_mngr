from aiogram.dispatcher.filters.state import StatesGroup, State


class Global(StatesGroup):
    not_started = State()
    waiting_for_action = State()


class GettingData(StatesGroup):
    choosing_account = State()
    accepting = State()


class DeleteDiscord(StatesGroup):
    choosing = State()


class DeleteTwitter(StatesGroup):
    choosing = State()


class AddingTwtAccount(StatesGroup):
    entering_data = State()
    choosing_discord = State()


class EditingAcc(StatesGroup):
    choosing_account = State()
    choosing_param = State()
    login = State()
    password = State()
    nickname = State()
    entering_changes = State()
    accepting_changes = State()


class EditingTwitter(StatesGroup):
    choosing_account = State()
    choosing_param = State()
    login = State()
    password = State()
    nickname = State()
    phone = State()
    entering_changes = State()
    accepting_changes = State()


class BulkAdd(StatesGroup):
    entering = State()
