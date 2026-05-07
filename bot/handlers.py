from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from states import UserForm
import uuid
import httpx
import os
import logging
import re
from datetime import datetime

router = Router()

def get_progress(current_state: str) -> str:
    """Format progress state with emojis and better visualization"""
    states = ['name', 'location', 'role', 'workplace', 'birth_date', 
              'goals', 'education', 'referral', 'phone_number']
    
    current_idx = states.index(current_state)
    
    # Create progress visualization
    progress = []
    for i, state in enumerate(states):
        if i < current_idx:
            progress.append("•")  # Completed steps (middle dot)
        elif i == current_idx:
            progress.append("◦")  # Current step (white bullet)
        else:
            progress.append(".")  # Future steps (ring operator)
    
    # Format current state name
    formatted_state = current_state.replace('_', ' ').title()
    
    return f"Progress: {' '.join(progress)}\nCurrent step: {formatted_state}"

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command"""
    args = message.text.split()[1:] if message.text else []
    
    if args and args[0].startswith('ref_'):
        # Store referral code
        referral_code = args[0][4:]  # Remove 'ref_' prefix
        await state.update_data(referral=referral_code)
        
    # Start registration process
    await message.answer(
        f"Welcome! Let's get you started.\n{get_progress('name')}\nWhat's your full name?",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(UserForm.name)

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = """
Available commands:
/start - Start or restart the registration process
/review - Review your entered information
/help - Show this help message
    """
    await message.answer(help_text)

@router.message(Command("review"))
async def cmd_review(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data:
        await message.answer("No information to review. Please start registration with /start")
        return
    
    review_text = "Here's your current information:\n\n"
    fields = {
        'name': 'Name',
        'location': 'Location',
        'role': 'Role',
        'workplace': 'Workplace',
        'birth_date': 'Birth Date',
        'goals': 'Goals',
        'education': 'Education',
        'referral': 'Referral',
        'phone_number': 'Phone Number'
    }
    
    for field, label in fields.items():
        if field in data:
            review_text += f"{label}: {data[field]}\n"
    
    current_state = await state.get_state()
    if current_state:
        review_text += f"\nCurrent progress: {get_progress(current_state.split(':')[1])}"
    
    await message.answer(review_text)

@router.message(UserForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"{get_progress('location')}\nPlease share your location.")
    await state.set_state(UserForm.location)

@router.message(UserForm.location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer(f"{get_progress('role')}\nWhat is your role/position?")
    await state.set_state(UserForm.role)

@router.message(UserForm.role)
async def process_role(message: types.Message, state: FSMContext):
    await state.update_data(role=message.text)
    await message.answer(f"{get_progress('workplace')}\nWhere do you work?")
    await state.set_state(UserForm.workplace)

@router.message(UserForm.workplace)
async def process_workplace(message: types.Message, state: FSMContext):
    await state.update_data(workplace=message.text)
    await message.answer(f"{get_progress('birth_date')}\nWhat is your birth date? (YYYY-MM-DD)")
    await state.set_state(UserForm.birth_date)

@router.message(UserForm.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    """Validate and process birth date in YYYY-MM-DD format"""
    date_str = message.text.strip()
    
    # Regular expression for YYYY-MM-DD format
    date_pattern = re.compile(r'^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$')
    
    if date_pattern.match(date_str):
        # Further validate the date is real
        year, month, day = map(int, date_str.split('-'))
        datetime(year, month, day)
    
        try:
            # Further validate the date is real
            year, month, day = map(int, date_str.split('-'))
            datetime(year, month, day)
            
            # Additional validation for reasonable year range
            current_year = datetime.now().year
            if not (1900 <= year <= current_year):
                raise ValueError("Year out of reasonable range")
                
            # Store valid date
            await state.update_data(birth_date=date_str)
            await message.answer(f"{get_progress('goals')}\nWhat are your goals?")
            await state.set_state(UserForm.goals)
            return
            
        except ValueError:
            pass
    await message.answer(
        "❌ Invalid date. Please enter a valid date in YYYY-MM-DD format\n"
        "For example: 1990-05-15"
    )

@router.message(UserForm.goals)
async def process_goals(message: types.Message, state: FSMContext):
    await state.update_data(goals=message.text)
    await message.answer(f"{get_progress('education')}\nWhat is your education background?")
    await state.set_state(UserForm.education)

@router.message(UserForm.education)
async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)

    referral = await state.get_value('referral')
    if referral is None:
        await message.answer(
            f"{get_progress('referral')}\nDo you have a referral ID? (Skip if none)",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Skip")]],
                resize_keyboard=True
            )
        )
    else:
        await message.answer(
            f"{get_progress('referral')}\nYour refferal ID: {referral}\nConfirm it or enter a new one or skip to continue without a referral.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Confirm"), KeyboardButton(text="Skip")]],
                resize_keyboard=True
            )
        )

    await state.set_state(UserForm.referral)

@router.message(UserForm.referral)
async def process_referral(message: types.Message, state: FSMContext):
    """Process referral code"""
    # Skip referral if user enters skip/none/no
    if message.text.lower() in ['skip', 'none', 'no']:
        await message.answer(
            f"{get_progress('phone_number')}\nLastly, please share your contact information.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Share Contact", request_contact=True)]],
                resize_keyboard=True
            )
        )
        await state.set_state(UserForm.phone_number)
        return

    referral = await state.get_value('referral')
    if referral is None:
        referral = message.text.strip()

    # Try to verify referral code
    try:
        BACKEND_URL = os.getenv("BACKEND_URL")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/users/verify-referral/{referral}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                # Store valid referral code and proceed
                await state.update_data(referral=referral)
                referrer_data = response.json()
                await message.answer(
                    f"✅ Referral code accepted! You were invited by {referrer_data['name']}.\n\n"
                    f"{get_progress('phone_number')}\n"
                    "Lastly, please share your contact information",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton(text="Share Contact", request_contact=True)]],
                        resize_keyboard=True
                    )
                )
                await state.set_state(UserForm.phone_number)
                return
            
    except Exception as e:
        logger.error(f"Error verifying referral: {e}")
    
    # If verification failed or errored, ask to try again or skip
    await message.answer(
        "❌ Invalid referral code. Please try again or type 'skip' to continue without a referral."
    )

@router.message(UserForm.phone_number)
async def process_phone(message: types.Message, state: FSMContext):
    if not message.contact:
        markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Share Contact", request_contact=True)]],
            resize_keyboard=True
        )
        await message.answer("Please share your contact using the button below", reply_markup=markup)
        return

    user_data = await state.get_data()
    user_data['phone_number'] = message.contact.phone_number
    user_data['telegram_id'] = message.from_user.id
    
    BACKEND_URL = os.getenv("BACKEND_URL")
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f'{BACKEND_URL}/api/users/',
                json=user_data,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                user_uuid = data["uuid"]
                webapp_url = f"{FRONTEND_URL}/user/{user_uuid}"
                
                if data["status"] == "existing":
                    await message.answer(
                        f"Welcome back! We found your existing account.\n"
                        f"Your unique ID: <code>{user_uuid}</code>\n"
                        f"Access your dashboard at: <a href='{webapp_url}'>{webapp_url}</a>",
                        reply_markup=types.ReplyKeyboardRemove(),
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                else:
                    await message.answer(
                        f"Thank you! Your registration is complete!\n"
                        f"Your unique ID: <code>{user_uuid}</code>\n"
                        f"Access your dashboard at: <a href='{webapp_url}'>{webapp_url}</a>",
                        reply_markup=types.ReplyKeyboardRemove(),
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                await state.clear()
            else:
                await message.answer("Sorry, there was an error saving your information. Please try again later.")
        except Exception as e:
            logging.error(f"Error communicating with backend: {e}")
            await message.answer("Sorry, there was an error connecting to the server. Please try again later.")
