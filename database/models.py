from sqlalchemy.sql.sqltypes import BLOB
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT, TINYINT
from sqlalchemy import Column, Integer, String, ForeignKey, Text, text, BigInteger
from sqlalchemy.orm import relationship
from config.logging_config import logger

from database.create_db import Base, Session, engine
from utils.consts.categories import CATEGORIES, CATEGORIES_EMOJI


class User(Base):
    __tablename__ = 'user'

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=False)
    last_personal_post_id = Column(SMALLINT(unsigned=True), default=0)

    user_channel_connection = relationship('UserChannel', back_populates='user_connection')
    user_category_connection = relationship('UserCategory', back_populates='user_connection')
    user_viewed_premium_post_connection = relationship('UserViewedPremiumPost', back_populates='user_connection')
    user_viewed_category_post_connection = relationship('UserViewedCategoryPost', back_populates='user_connection')
    user_viewed_personal_post_connection = relationship('UserViewedPersonalPost', back_populates='user_connection')

    def __repr__(self):
        return f"<User(id={self.id}, last_post_id={self.last_post_id})>"


class UserChannel(Base):
    __tablename__ = 'user_channel'

    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.id'), primary_key=True)
    channel_id = Column(INTEGER(unsigned=True), ForeignKey('personal_channel.id'), primary_key=True)

    user_connection = relationship('User', back_populates='user_channel_connection')
    personal_channel_connection = relationship('PersonalChannel', back_populates='user_channel_connection')

    def __repr__(self):
        return f"<UserChannel(user_id={self.user_id}, channel_id={self.channel_id})>"


class PersonalChannel(Base):
    __tablename__ = 'personal_channel'

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    coefficient = Column(SMALLINT(unsigned=True), default=1)

    user_channel_connection = relationship('UserChannel', back_populates='personal_channel_connection')
    personal_post_connection = relationship('PersonalPost', back_populates='personal_channel_connection')

    def __repr__(self):
        return f"<PersonalChannel(id={self.id}, tg_id={self.tg_id} username={self.username})>"


class PersonalPost(Base):
    __tablename__ = 'personal_post'

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    text = Column(Text)
    image_path = Column(Text)
    entities = Column(BLOB)
    personal_channel_id = Column(INTEGER(unsigned=True), ForeignKey('personal_channel.id'))
    likes = Column(INTEGER(unsigned=True), default=0)
    dislikes = Column(INTEGER(unsigned=True), default=0)

    personal_channel_connection = relationship('PersonalChannel', back_populates='personal_post_connection')
    user_viewed_personal_post_connection = relationship('UserViewedPersonalPost', back_populates='personal_post_connection')

    def __repr__(self):
        return f"<PersonalPost(id={self.id}, text={self.text}, image_path={self.image_path}, entities={self.entities}, likes={self.likes}, dislikes={self.dislikes})>"


class UserCategory(Base):
    __tablename__ = 'user_category'

    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.id'), primary_key=True)
    category_id = Column(TINYINT(unsigned=True), ForeignKey('category.id'), primary_key=True)

    user_connection = relationship('User', back_populates='user_category_connection')
    category_connection = relationship('Category', back_populates='user_category_connection')


class Category(Base):
    __tablename__ = 'category'

    id = Column(TINYINT(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(30), unique=True, nullable=False)
    emoji = Column(String(10), nullable=False)

    user_category_connection = relationship('UserCategory', back_populates='category_connection')
    category_channel_connection = relationship('CategoryChannel', back_populates='category_connection')

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, emoji={self.emoji})>"


class PremiumChannel(Base):
    __tablename__ = 'premium_channel'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    tg_id = Column(BigInteger, nullable=False)
    username = Column(String(32), unique=True, nullable=False)
    coefficient = Column(TINYINT(unsigned=True), default=2)

    premium_post_connection = relationship('PremiumPost', back_populates='premium_channel_connection')

    def __repr__(self):
        return f"<PremiumChannel(id={self.id}, username={self.username}, tg_id={self.tg_id})>"


class PremiumPost(Base):
    __tablename__ = 'premium_post'

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    text = Column(Text)
    image_path = Column(Text)
    entities = Column(BLOB)
    likes = Column(Integer)
    dislikes = Column(Integer)
    premium_channel_id = Column(INTEGER(unsigned=True), ForeignKey("premium_channel.id"))

    premium_channel_connection = relationship('PremiumChannel', back_populates='premium_post_connection')
    user_viewed_premium_post_connection = relationship('UserViewedPremiumPost', back_populates='premium_post_connection')

    def __repr__(self):
        return f"<PremiumPost(id={self.id}, text={self.text}, image_path={self.image_path}, likes={self.likes},dislikes={self.dislikes})>"


class CategoryChannel(Base):
    __tablename__ = 'category_channel'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    tg_id = Column(BigInteger, nullable=False)
    username = Column(String(32), unique=True, nullable=False)
    category_id = Column(TINYINT(unsigned=True), ForeignKey("category.id"), nullable=False)
    coefficient = Column(TINYINT(unsigned=True), default=1)

    category_connection = relationship('Category', back_populates='category_channel_connection')
    category_post_connection = relationship('CategoryPost', back_populates='category_channel_connection')

    def __repr__(self):
        return f"<CategoryChannel(id={self.id}, tg_id={self.tg_id}, username={self.username}, category_id={self.category_id})>"


class CategoryPost(Base):
    __tablename__ = 'category_post'

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    text = Column(Text)
    image_path = Column(Text)
    entities = Column(BLOB)
    likes = Column(Integer)
    dislikes = Column(Integer)
    category_channel_id = Column(INTEGER(unsigned=True), ForeignKey("category_channel.id"))

    category_channel_connection = relationship('CategoryChannel', back_populates='category_post_connection')
    user_viewed_category_post_connection = relationship('UserViewedCategoryPost', back_populates='category_post_connection')

    def __repr__(self):
        return f"<CategoryPost(id={self.id}, text={self.text}, image_path={self.image_path}, likes={self.likes}, dislikes={self.dislikes}, category_channel_id={self.category_channel_id})>"


class MarkType(Base):
    __tablename__ = 'mark_type'

    id = Column(TINYINT(unsigned=True), primary_key=True)
    name = Column(String(10), unique=True)

    user_viewed_premium_post_connection = relationship("UserViewedPremiumPost", back_populates="mark_type_connection")
    user_viewed_category_post_connection = relationship('UserViewedCategoryPost', back_populates='mark_type_connection')
    user_viewed_personal_post_connection = relationship('UserViewedPersonalPost', back_populates='mark_type_connection')

    def __repr__(self):
        return f"<MarkType(id={self.id}, name={self.name})>"


class UserViewedPremiumPost(Base):
    __tablename__ = 'user_viewed_premium_post'

    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.id'), primary_key=True)
    premium_post_id = Column(INTEGER(unsigned=True), ForeignKey('premium_post.id'), primary_key=True)
    mark_type_id = Column(TINYINT(unsigned=True), ForeignKey('mark_type.id'), default=3)

    user_connection = relationship("User", back_populates="user_viewed_premium_post_connection")
    premium_post_connection = relationship("PremiumPost", back_populates="user_viewed_premium_post_connection")
    mark_type_connection = relationship("MarkType", back_populates="user_viewed_premium_post_connection")

    def __repr__(self):
        return f"<UserViewedPremiumPost(user_id={self.user_id}, premium_post_id={self.premium_post_id}, mark_type_id={self.mark_type_id})>"


class UserViewedCategoryPost(Base):
    __tablename__ = 'user_viewed_category_post'

    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.id'), primary_key=True)
    category_post_id = Column(INTEGER(unsigned=True), ForeignKey('category_post.id'), primary_key=True)
    mark_type_id = Column(TINYINT(unsigned=True), ForeignKey('mark_type.id'), default=3)

    user_connection = relationship("User", back_populates="user_viewed_category_post_connection")
    category_post_connection = relationship("CategoryPost", back_populates="user_viewed_category_post_connection")
    mark_type_connection = relationship("MarkType", back_populates="user_viewed_category_post_connection")

    def __repr__(self):
        return f"<UserViewedCategoryPost(user_id={self.user_id}, premium_post_id={self.premium_post_id}, mark_type_id={self.mark_type_id}>"


class UserViewedPersonalPost(Base):
    __tablename__ = 'user_viewed_personal_post'

    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.id'), primary_key=True)
    personal_post_id = Column(INTEGER(unsigned=True), ForeignKey('personal_post.id'), primary_key=True)
    mark_type_id = Column(TINYINT(unsigned=True), ForeignKey('mark_type.id'), default=3)

    user_connection = relationship("User", back_populates="user_viewed_personal_post_connection")
    personal_post_connection = relationship('PersonalPost', back_populates='user_viewed_personal_post_connection')
    mark_type_connection = relationship("MarkType", back_populates="user_viewed_personal_post_connection")

    def __repr__(self):
        return f"<UserViewedCategoryPost(user_id={self.user_id}, premium_post_id={self.premium_post_id}, mark_type_id={self.mark_type_id}>"


# Пересоздаёт бд
#
# Base.metadata.drop_all(engine, checkfirst=True)
# Base.metadata.create_all(engine)

session = Session()
query = "SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'"
session.execute(text(query))
session.commit()


def create_base_data():
    session = Session()
    for i in range(0, len(CATEGORIES)):
        try:
            new_category = Category(id=i + 1, name=CATEGORIES[i], emoji=f'{CATEGORIES_EMOJI[CATEGORIES[i]]}')
            session.add(new_category)
            session.flush()
            new_mark_type = MarkType(name='like')
            session.add(new_mark_type)
            new_mark_type = MarkType(name='dislike')
            session.add(new_mark_type)
            new_mark_type = MarkType(name='neutral')
            session.add(new_mark_type)
            session.flush()
        except Exception as err:
            session.rollback()
            logger.error(err)


create_base_data()
