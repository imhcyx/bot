from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, User, Nine

from config import cfg

engine = create_engine(cfg['db'])

Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    session = Session()
    uid = cfg['admin_id']
    if session.query(User).filter_by(id=uid).count() == 0:
        # adminstrator
        print('add administrator ...')
        admin = User(id=uid, level=5)
        session.add(admin)
        session.commit()
        # nine-calc data import
        print('import nine-calc data ...')
        with open('9.txt', 'r') as f:
            try:
                while True:
                    s = f.readline().strip()
                    if s:
                        num = int(s.split('=')[0])
                        nine = Nine(number=num, answer=s)
                        session.add(nine)
                    else:
                        break
            finally:
                session.commit()
    session.close()
