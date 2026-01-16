from core.database import engine
from trading.models import Base

Base.metadata.create_all(bind=engine)
