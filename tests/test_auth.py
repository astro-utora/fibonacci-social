#%%
# %cd ..
#%%
import pytest
import os
from dotenv import load_dotenv
from backend.app.routers.auth import verify_telegram_data

# Load environment variables from .env file
load_dotenv()

def test_verify_telegram_data():
    # Test data from requests.http
    test_data = {
        "id": 1562163,
        "first_name": "Stanislav",
        "last_name": "Kapulkin",
        "username": "stask",
        "photo_url": "https://t.me/i/userpic/320/fogjxH0mqSEffNsNlWZGz_Z8mHfumLzTTJYkyHN3x4c.jpg",
        "auth_date": 1738927294,
    }

    test_hash = "16c286fba7dc6390dfc887469a96d1e2e1c9ac8b9c1409d574450b8c22fb9db5"
    
    # Get bot token from .env
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        pytest.skip("TELEGRAM_BOT_TOKEN not found in .env")
    
    # Verify the data
    assert verify_telegram_data(test_data, test_hash) == True

def test_verify_telegram_data_invalid_hash():
    test_data = {
        "id": 1562163,
        "first_name": "Stanislav",
        "last_name": "Kapulkin",
        "username": "stask",
        "photo_url": "https://t.me/i/userpic/320/fogjxH0mqSEffNsNlWZGz_Z8mHfumLzTTJYkyHN3x4c.jpg",
        "auth_date": 1738927294,
    }
    
    invalid_hash = "invalid_hash"
    
    # Get bot token from .env
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        pytest.skip("TELEGRAM_BOT_TOKEN not found in .env")
    
    # Verify the data should fail with invalid hash
    assert verify_telegram_data(test_data, invalid_hash) == False 

#%%
# test_verify_telegram_data()
# %%
