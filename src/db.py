from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, User, Nine

engine = create_engine('sqlite:///bot.db')

Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    session = Session()
    if session.query(User).filter_by(id=907308901).count() == 0:
        admin = User(id=907308901, level=5)
        session.add(admin)
        session.commit()
    with open('9.txt', 'r') as f:
        try:
            while True:
                s = f.readline().strip()
                if s:
                    num = int(s.split('=')[0])
                    if session.query(Nine).filter_by(number=num).count() == 0:
                        nine = Nine(number=num, answer=s)
                        session.add(nine)
                else:
                    break
        finally:
            session.commit()
