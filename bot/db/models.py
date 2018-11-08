from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer)
    bt_user = Column(String(20))
    bt_cookie = Column(String(100))
    create_time = Column(DateTime, default=datetime.now())
    modify_time = Column(DateTime, default=datetime.now())
    notify_level = Column(Integer, default=0)


class TorrentSimple(Base):
    __tablename__ = 'torrent_page_50'
    id = Column(Integer, primary_key=True)
    torrent_id = Column(Integer)
    torrent_name = Column(String(100))
    torrent_link = Column(String(100))
    page = Column(Integer)
