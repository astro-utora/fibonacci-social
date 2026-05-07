from aiogram.fsm.state import State, StatesGroup

class UserForm(StatesGroup):
    name = State()
    location = State()
    role = State()
    workplace = State()
    birth_date = State()
    goals = State()
    education = State()
    referral = State()
    phone_number = State() 