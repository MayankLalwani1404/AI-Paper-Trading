from backend.core.database import engine
from backend.trading.models import Base

Base.metadata.create_all(bind=engine)
