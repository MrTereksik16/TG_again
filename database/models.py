from sqlalchemy.sql.sqltypes import BLOB
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.create_db import Base, engine


class User(Base):
    __tablename__ = 'user'

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=False)

    user_channel_connection = relationship('UserChannel', cascade='all, delete', back_populates='user_connection')
    user_category_connection = relationship('UserCategory', cascade='all, delete', back_populates='user_connection')
    user_viewed_premium_post_connection = relationship('UserViewedPremiumPost', cascade='all, delete', back_populates='user_connection')
    user_viewed_category_post_connection = relationship('UserViewedCategoryPost', cascade='all, delete', back_populates='user_connection')
    user_viewed_personal_post_connection = relationship('UserViewedPersonalPost', cascade='all, delete', back_populates='user_connection')

    def __repr__(self):
        return f'<User(id={self.id}, last_post_id={self.last_post_id})>'


class UserChannel(Base):
    __tablename__ = 'user_channel'

    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    channel_id = Column(BIGINT(unsigned=True), ForeignKey('personal_channel.id', ondelete='CASCADE'), primary_key=True)

    user_connection = relationship('User', back_populates='user_channel_connection')
    personal_channel_connection = relationship('PersonalChannel', back_populates='user_channel_connection')

    def __repr__(self):
        return f'<UserChannel(user_id={self.user_id}, channel_id={self.channel_id})>'


class PersonalChannel(Base):
    __tablename__ = 'personal_channel'

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=False)
    username = Column(String(100), unique=True, nullable=False)
    coefficient = Column(TINYINT(unsigned=True), ForeignKey('coefficient.value', ondelete='CASCADE'), default=1)

    user_channel_connection = relationship('UserChannel', cascade='all, delete', back_populates='personal_channel_connection')
    personal_post_connection = relationship('PersonalPost', cascade='all, delete', back_populates='personal_channel_connection')
    coefficient_connection = relationship('Coefficient', cascade='all, delete', back_populates='personal_channel_connection')

    def __repr__(self):
        return f'<PersonalChannel(id={self.id}, tg_id={self.tg_id} username={self.username}, coefficient={self.coefficient})>'


class PersonalPost(Base):
    __tablename__ = 'personal_post'

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    text = Column(Text)
    media_path = Column(Text)
    entities = Column(BLOB)
    personal_channel_id = Column(BIGINT(unsigned=True), ForeignKey('personal_channel.id', ondelete='CASCADE'))
    likes = Column(INTEGER(unsigned=True), default=0)
    dislikes = Column(INTEGER(unsigned=True), default=0)

    personal_channel_connection = relationship('PersonalChannel', back_populates='personal_post_connection')
    user_viewed_personal_post_connection = relationship('UserViewedPersonalPost', cascade='all, delete', back_populates='personal_post_connection')

    def __repr__(self):
        return f'<PersonalPost(id={self.id}, text={self.text}, media_path={self.media_path}, entities={self.entities}, likes={self.likes}, dislikes={self.dislikes})>'


class UserCategory(Base):
    __tablename__ = 'user_category'

    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    category_id = Column(TINYINT(unsigned=True), ForeignKey('category.id', ondelete='CASCADE'), primary_key=True)

    user_connection = relationship('User', back_populates='user_category_connection')
    category_connection = relationship('Category', back_populates='user_category_connection')


class Category(Base):
    __tablename__ = 'category'

    id = Column(TINYINT(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(30), unique=True, nullable=False)
    emoji = Column(String(10), nullable=False)

    user_category_connection = relationship('UserCategory', cascade='all, delete', back_populates='category_connection')
    category_channel_connection = relationship('CategoryChannel', cascade='all, delete', back_populates='category_connection')

    def __repr__(self):
        return f'<Category(id={self.id}, name={self.name}, emoji={self.emoji})>'


class PremiumChannel(Base):
    __tablename__ = 'premium_channel'

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=False)
    username = Column(String(32), unique=True, nullable=False)
    coefficient = Column(TINYINT(unsigned=True), ForeignKey('coefficient.value', ondelete='CASCADE'), default=2)

    premium_post_connection = relationship('PremiumPost', cascade='all, delete', back_populates='premium_channel_connection')
    coefficient_connection = relationship('Coefficient', cascade='all, delete', back_populates='premium_channel_connection')

    def __repr__(self):
        return f'<PremiumChannel(id={self.id}, username={self.username} coefficient={self.coefficient})>'


class PremiumPost(Base):
    __tablename__ = 'premium_post'

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    text = Column(Text)
    media_path = Column(Text)
    entities = Column(BLOB)
    likes = Column(Integer)
    dislikes = Column(Integer)
    views = Column(INTEGER(unsigned=True), default=0)
    report_message_id = Column(INTEGER(unsigned=True), default=None)
    premium_channel_id = Column(BIGINT(unsigned=True), ForeignKey('premium_channel.id', ondelete='CASCADE'))

    premium_channel_connection = relationship('PremiumChannel', back_populates='premium_post_connection')
    user_viewed_premium_post_connection = relationship('UserViewedPremiumPost', cascade='all, delete', back_populates='premium_post_connection')

    def __repr__(self):
        return f'<PremiumPost(id={self.id}, text={self.text}, media_path={self.media_path}, likes={self.likes},dislikes={self.dislikes})>'


class CategoryChannel(Base):
    __tablename__ = 'category_channel'

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=False)
    username = Column(String(32), unique=True, nullable=False)
    category_id = Column(TINYINT(unsigned=True), ForeignKey('category.id', ondelete='CASCADE'), nullable=False)
    coefficient = Column(TINYINT(unsigned=True), ForeignKey('coefficient.value', ondelete='CASCADE'), default=1)

    category_connection = relationship('Category', back_populates='category_channel_connection')
    category_post_connection = relationship('CategoryPost', cascade='all, delete', back_populates='category_channel_connection')
    coefficient_connection = relationship('Coefficient', cascade='all, delete', back_populates='category_channel_connection')

    def __repr__(self):
        return f'<CategoryChannel(id={self.id}, tg_id={self.tg_id}, username={self.username}, category_id={self.category_id})>'


class CategoryPost(Base):
    __tablename__ = 'category_post'

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    text = Column(Text)
    media_path = Column(Text)
    entities = Column(BLOB)
    likes = Column(Integer)
    dislikes = Column(Integer)
    views = Column(INTEGER(unsigned=True), default=0)
    report_message_id = Column(INTEGER(unsigned=True), default=None)
    category_channel_id = Column(BIGINT(unsigned=True), ForeignKey('category_channel.id', ondelete='CASCADE'))

    category_channel_connection = relationship('CategoryChannel', back_populates='category_post_connection')
    user_viewed_category_post_connection = relationship('UserViewedCategoryPost', cascade='all, delete', back_populates='category_post_connection')

    def __repr__(self):
        return f'<CategoryPost(id={self.id}, text={self.text}, media_path={self.media_path}, likes={self.likes}, dislikes={self.dislikes}, category_channel_id={self.category_channel_id})>'


class MarkType(Base):
    __tablename__ = 'mark_type'

    id = Column(TINYINT(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(10), unique=True)

    user_viewed_premium_post_connection = relationship('UserViewedPremiumPost', cascade='all, delete', back_populates='mark_type_connection')
    user_viewed_category_post_connection = relationship('UserViewedCategoryPost', cascade='all, delete', back_populates='mark_type_connection')
    user_viewed_personal_post_connection = relationship('UserViewedPersonalPost', cascade='all, delete', back_populates='mark_type_connection')

    def __repr__(self):
        return f'<MarkType(id={self.id}, name={self.name})>'


class UserViewedPremiumPost(Base):
    __tablename__ = 'user_viewed_premium_post'

    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    premium_post_id = Column(BIGINT(unsigned=True), ForeignKey('premium_post.id', ondelete='CASCADE'), primary_key=True)
    mark_type_id = Column(TINYINT(unsigned=True), ForeignKey('mark_type.id', ondelete='CASCADE'), default=3)
    counter = Column(TINYINT(unsigned=True), default=15)

    user_connection = relationship('User', back_populates='user_viewed_premium_post_connection')
    premium_post_connection = relationship('PremiumPost', back_populates='user_viewed_premium_post_connection')
    mark_type_connection = relationship('MarkType', back_populates='user_viewed_premium_post_connection')

    def __repr__(self):
        return f'<UserViewedPremiumPost(user_id={self.user_id}, premium_post_id={self.premium_post_id}, mark_type_id={self.mark_type_id})>'


class UserViewedCategoryPost(Base):
    __tablename__ = 'user_viewed_category_post'

    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    category_post_id = Column(BIGINT(unsigned=True), ForeignKey('category_post.id', ondelete='CASCADE'), primary_key=True)
    mark_type_id = Column(TINYINT(unsigned=True), ForeignKey('mark_type.id', ondelete='CASCADE'), default=3)
    counter = Column(TINYINT(unsigned=True), default=15)

    user_connection = relationship('User', back_populates='user_viewed_category_post_connection')
    category_post_connection = relationship('CategoryPost', back_populates='user_viewed_category_post_connection')
    mark_type_connection = relationship('MarkType', back_populates='user_viewed_category_post_connection')

    def __repr__(self):
        return f'<UserViewedCategoryPost(user_id={self.user_id}, premium_post_id={self.premium_post_id}, mark_type_id={self.mark_type_id}>'


class UserViewedPersonalPost(Base):
    __tablename__ = 'user_viewed_personal_post'

    user_id = Column(BIGINT(unsigned=True), ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    personal_post_id = Column(BIGINT(unsigned=True), ForeignKey('personal_post.id', ondelete='CASCADE'), primary_key=True)
    mark_type_id = Column(TINYINT(unsigned=True), ForeignKey('mark_type.id', ondelete='CASCADE'), default=3)

    user_connection = relationship('User', back_populates='user_viewed_personal_post_connection')
    personal_post_connection = relationship('PersonalPost', back_populates='user_viewed_personal_post_connection')
    mark_type_connection = relationship('MarkType', back_populates='user_viewed_personal_post_connection')

    def __repr__(self):
        return f'<UserViewedCategoryPost(user_id={self.user_id}, premium_post_id={self.premium_post_id}, mark_type_id={self.mark_type_id}>'


class Coefficient(Base):
    __tablename__ = 'coefficient'

    value = Column(TINYINT(unsigned=True), primary_key=True, nullable=False)

    premium_channel_connection = relationship('PremiumChannel', cascade='all, delete', back_populates='coefficient_connection')
    personal_channel_connection = relationship('PersonalChannel', cascade='all, delete', back_populates='coefficient_connection')
    category_channel_connection = relationship('CategoryChannel', cascade='all, delete', back_populates='coefficient_connection')

    def __repr__(self):
        return f'<Coefficient(value={self.value})>'

# Пересоздаёт бд
# Base.metadata.drop_all(engine, checkfirst=True)
# Base.metadata.create_all(engine)
