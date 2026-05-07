from typing import List
from sqlalchemy.orm import relationship

class User(Base):
    # ... existing fields ...
    
    # Add relationship
    fillout_submissions = relationship("FilloutSubmission", back_populates="user") 