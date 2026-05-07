from app.database import SessionLocal
from app.models import UserDB, UserRoleDB, AuthUser, EmailUser, AuthProvider
from uuid import uuid4
import bcrypt

def seed_test_data():
    db = SessionLocal()
    try:
        # Create test user
        test_user = UserDB(
            uuid=uuid4(),
            name="Test User",
            location="Test City",
            workplace="Test Company",
            birth_date="1990-01-01",
            goals="Professional growth",
            education="University",
            referral_code="TEST123"
        )
        db.add(test_user)
        db.flush()

        # Create auth user
        auth_user = AuthUser(
            user_uuid=test_user.uuid,
            provider=AuthProvider.EMAIL
        )
        db.add(auth_user)
        db.flush()

        # Create email user
        password_hash = bcrypt.hashpw("user123".encode(), bcrypt.gensalt()).decode()
        email_user = EmailUser(
            auth_id=auth_user.id,
            email="user@example.com",
            password_hash=password_hash,
            is_verified=True
        )
        db.add(email_user)

        # Add roles
        roles = ["Management", "Development", "Frontend"]
        for role in roles:
            user_role = UserRoleDB(
                user_id=test_user.uuid,
                role=role
            )
            db.add(user_role)

        db.commit()
        print("Test data seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding test data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_data() 