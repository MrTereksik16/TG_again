from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import create_database, database_exists
from config import config

Base = declarative_base()
database_properties = f'{config.DATABASE_USER}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}/{config.DATABASE_NAME}'
engine = create_engine(f'mysql+pymysql://{database_properties}', echo=True)
if not database_exists(engine.url):
    create_database(engine.url, 'utf8mb4')

Session = sessionmaker(bind=engine)
