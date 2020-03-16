from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, User

engine = create_engine('sqlite:///bot.db')

Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    session = Session()
    if session.query(User).filter_by(id=907308901).count() == 0:
        admin = User(id=907308901, level=5)
        session.add(admin)
        session.commit()
