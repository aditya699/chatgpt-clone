from app.database import Base, engine
from app.auth.models import User  # Import all models here

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)