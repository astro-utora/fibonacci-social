// Message 1.

Create a webapp with onboarding through telegram chat with an aiogram bot.

## Aigoram 
Aigoram bot:
 - asks user for basic information: name, geo location, role, workplace, birth date, goals, education
 - asks about refferal id
 - requests user to share his phone number linked to the telegram account to link app account to the number as a final step
 - as soon, as information is provided, generates a unique uuid and sends it to the user within welcome message to the full webapp

Aigoram bot should initially gently ask about information step by step and show progress with dots like: . . current_field . . . - two fields are filled, three are next

/start command with confirmation can be used to reset the progress and start from the beginning with corresponding message

/revew allows to review entered informaton

Provide /help command.

## Webapp
Backend accepts information from telegram bot backend and generates uuid for the bot

Creates infividual dashboard for each user with url /user/<generated uuid>

Dashboard displays entered by user information

Use FastAPI and Vue 3 for Webapp


// Message 2.
take BOT_TOKEN from .env file

// Message 3.
Is everython implemented according to description and your recommendations or something is remaining? 

// Message 4.
Is everything for backend, frontend and backend-bot communication / backend-frontent communication is implemented ?

// Message 5.
bot-backend communication should be inversed - backend generates uuid by request and sends it to the bot
