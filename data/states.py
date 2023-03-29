from aiogram.dispatcher.filters.state import StatesGroup, State


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
    choosing_discord = State()


class EditingAcc(StatesGroup):
    choosing_account = State()
    choosing_param = State()
    entering_changes = State()
    accepting_changes = State()
