"""FastAPI dependencies for dependency injection."""
from typing import Generator
from sqlalchemy.orm import Session

import config
from database.Database import APIDatabase


def get_db() -> Generator[Session, None, None]:
    """
    Get database session using dependency injection.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = APIDatabase(config.DB_URL)
    try:
        yield db
    finally:
        db.close()
