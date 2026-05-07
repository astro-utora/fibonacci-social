import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import UserDB, UserRoleDB
from uuid import uuid4, UUID
from .seed_role_tree import seed_role_tree

def seed_data():
    db = SessionLocal()
    try:
        # Create user roles for admin
        admin_user = db.query(UserDB).first()  # Get the first user (admin)
        if admin_user:
            create_user_roles(db, admin_user.uuid)

        # Add role tree seeding
        seed_role_tree(db)

        db.commit()
        print("Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

def create_user_roles(db: Session, user_id: UUID):
    """Create initial roles for user"""
    roles = [
        UserRoleDB(
            user_id=user_id,
            role="Management"
        ),
        UserRoleDB(
            user_id=user_id,
            role="Development"
        )
    ]
    for role in roles:
        db.add(role)
    db.flush()

if __name__ == "__main__":
    seed_data() 