from app.database import SessionLocal
from app.models import RoleNode  # Import from models package
from uuid import uuid4

def seed_role_tree():
    db = SessionLocal()
    try:
        # Clear existing tree
        db.query(RoleNode).delete()
        
        # Create sample tree
        root = RoleNode(
            id=str(uuid4()),
            role="Organization",
            fillout_id=None
        )
        db.add(root)
        db.flush()

        # Management branch
        management = RoleNode(
            id=str(uuid4()),
            role="Management",
            fillout_id="mgmt-form-1",
            parent_id=root.id
        )
        db.add(management)
        db.flush()

        team_lead = RoleNode(
            id=str(uuid4()),
            role="Team Lead",
            fillout_id="team-lead-form",
            parent_id=management.id
        )
        db.add(team_lead)

        # Development branch
        development = RoleNode(
            id=str(uuid4()),
            role="Development",
            fillout_id=None,
            parent_id=root.id
        )
        db.add(development)
        db.flush()

        frontend = RoleNode(
            id=str(uuid4()),
            role="Frontend",
            fillout_id="frontend-form",
            parent_id=development.id
        )
        db.add(frontend)

        backend = RoleNode(
            id=str(uuid4()),
            role="Backend",
            fillout_id="backend-form",
            parent_id=development.id
        )
        db.add(backend)

        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_role_tree() 