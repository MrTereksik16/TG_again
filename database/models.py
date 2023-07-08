from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database
from config import config

Base = declarative_base()
database_properties = f'{config.DATABASE_USER}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}/{config.DATABASE_NAME}'
engine = create_engine(f'mysql+pymysql://{database_properties}', echo=True)
if not database_exists(engine.url):
    create_database(engine.url)

# Создаем сессию, чтобы выполнять операции с базой данных
Session = sessionmaker(bind=engine)

session = Session()


class User(Base):
    __tablename__ = 'user'

    user_tg_id = Column(Integer, primary_key=True)
    last_post_id = Column(Integer)

    user_channel_connection = relationship('UserChannel', back_populates='user_connection')
    user_category_connection = relationship('UserCategory', back_populates='user_connection')

    def __repr__(self):
        return f"<User(user_tg_id='{self.user_tg_id}', last_post_id='{self.last_post_id}')>"


class UserChannel(Base):
    __tablename__ = 'user_channel'
    user_id = Column(Integer, ForeignKey('user.user_tg_id'), primary_key=True)
    channel_id = Column(Integer, ForeignKey('personal_channel.id'), primary_key=True)

    user_connection = relationship('User', back_populates='user_channel_connection')

    personal_channel_connection = relationship('PersonalChannel', back_populates='user_channel_connection')

    def __repr__(self):
        return f"<User_Channel(user_id='{self.user_id}', channel_id='{self.channel_id}')>"


class PersonalChannel(Base):
    __tablename__ = 'personal_channel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)

    user_channel_connection = relationship('UserChannel', back_populates='personal_channel_connection')

    personal_post_connection = relationship('PersonalPost', back_populates='personal_channel_connection')

    def __repr__(self):
        return f"<PersonalChannel(id='{self.id}', username='{self.username}')>"


class PersonalPost(Base):
    __tablename__ = 'personal_post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(100))
    image_path = Column(String(100))
    channel_id = Column(Integer, ForeignKey('personal_channel.id'))

    personal_channel_connection = relationship('PersonalChannel', back_populates='personal_post_connection')

    def __repr__(self):
        return f"<PersonalPost(text='{self.text}', image_path='{self.image_path}')>"


class UserCategory(Base):
    __tablename__ = 'user_category'
    user_id = Column(Integer, ForeignKey('user.user_tg_id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'), primary_key=True)

    user_connection = relationship('User', back_populates='user_category_connection')
    category_connection = relationship('Category', back_populates='user_category_connection')


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

    user_category_connection = relationship('UserCategory', back_populates='category_connection')
    general_channel_connection = relationship('GeneralChannel', back_populates='category_connection')

    def __repr__(self):
        return f"<Category(name='{self.name}')>"


class GeneralChannel(Base):
    __tablename__ = 'general_channel'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    category_id = Column(Integer, ForeignKey('category.id'))

    category_connection = relationship('Category', back_populates='general_channel_connection')
    general_post_connection = relationship('GeneralPost', back_populates='general_channel_connection')

    def __repr__(self):
        return f"<GeneralChannels(username='{self.username}')>"


class GeneralPost(Base):
    __tablename__ = 'general_post'
    id = Column(Integer, primary_key=True)
    text = Column(String(50))
    image_path = Column(String(50))
    likes = Column(Integer)
    dislikes = Column(Integer)
    general_channel_id = Column(Integer, ForeignKey("general_channel.id"))

    general_channel_connection = relationship('GeneralChannel', back_populates='general_post_connection')

    def __repr__(self):
        return f"<GeneralPost(text='{self.text}', image_path='{self.image_path}', likes='{self.likes}', dislikes='{self.dislikes}')>"


session.commit()
session.close()
