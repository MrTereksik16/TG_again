from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()

engine = create_engine('mysql+pymysql://root:ePPXyiUis-2309@localhost/again', echo=True)
if not database_exists(engine.url):
    create_database(engine.url)

# Создаем сессию, чтобы выполнять операции с базой данных
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'user'

    user_tg_id = Column(Integer, primary_key=True)
    last_post_id = Column(Integer)

    user_channels_connection = relationship('User_Channels', back_populates='user_connection')
    user_categories_connection = relationship('User_Categories', back_populates='user_connection')

    def __repr__(self):
        return f"<User(user_tg_id='{self.user_tg_id}', last_post_id='{self.last_post_id}')>"


class User_Channels(Base):
    __tablename__ = 'user_channels'
    user_id = Column(Integer, ForeignKey('user.user_tg_id'), primary_key=True)
    channel_id = Column(Integer, ForeignKey('personal_channels.id'), primary_key=True)

    user_connection = relationship('User', back_populates='user_channels_connection')

    personal_channels_connection = relationship('Personal_Channels', back_populates='user_channels_connection')

    def __repr__(self):
        return f"<User_Channels(user_id='{self.user_id}', channel_id='{self.channel_id}')>"


class Personal_Channels(Base):
    __tablename__ = 'personal_channels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)

    user_channels_connection = relationship('User_Channels', back_populates='personal_channels_connection')

    personal_posts_connection = relationship('Personal_Posts', back_populates='personal_channels_connection')

    def __repr__(self):
        return f"<Personal_Channels(id='{self.id}', username='{self.username}')>"


class Personal_Posts(Base):
    __tablename__ = 'personal_posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(100))
    image_path = Column(String(100))
    channel_id = Column(Integer, ForeignKey('personal_channels.id'))

    personal_channels_connection = relationship('Personal_Channels', back_populates='personal_posts_connection')

    def __repr__(self):
        return f"<Personal_Posts(text='{self.text}', image_path='{self.image_path}')>"


class User_Categories(Base):
    __tablename__ = 'user_categories'
    user_id = Column(Integer, ForeignKey('user.user_tg_id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)

    user_connection = relationship('User', back_populates='user_categories_connection')
    categories_connection = relationship('Categories', back_populates='user_categories_connection')


class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

    user_categories_connection = relationship('User_Categories', back_populates='categories_connection')
    general_channels_connection = relationship('General_Channels', back_populates='categories_connection')

    def __repr__(self):
        return f"<Categories(name='{self.name}')>"


class General_Channels(Base):
    __tablename__ = 'general_channels'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    category_id = Column(Integer, ForeignKey('categories.id'))

    categories_connection = relationship('Categories', back_populates='general_channels_connection')
    general_posts_connection = relationship('General_Posts', back_populates='general_channels_connection')

    def __repr__(self):
        return f"<General_Channels(username='{self.username}')>"


class General_Posts(Base):
    __tablename__ = 'general_posts'
    id = Column(Integer, primary_key=True)
    text = Column(String(50))
    image_path = Column(String(50))
    likes = Column(Integer)
    dislikes = Column(Integer)
    general_channel_id = Column(Integer, ForeignKey("general_channels.id"))

    general_channels_connection = relationship('General_Channels', back_populates='general_posts_connection')

    def __repr__(self):
        return f"<General_Posts(text='{self.text}', image_path='{self.image_path}', likes='{self.likes}', dislikes='{self.dislikes}')>"


session.commit()
