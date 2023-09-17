from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import config

DATABASE_URL = f'mysql+pymysql://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}/{config.DATABASE_NAME}'
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
