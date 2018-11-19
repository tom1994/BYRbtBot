from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
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
    stream_status = Column(Integer, default=0)
    comm_num = Column(Integer, default=0)


class TorrentSimple(Base):
    __tablename__ = 'torrent_page_50'
    id = Column(Integer, primary_key=True)
    torrent_id = Column(Integer)
    torrent_name = Column(Text)
    torrent_link = Column(String(100))
    page = Column(Integer)
    torrent_download_link = Column(String(100))
    torrent_up_num = Column(Integer)
    torrent_down_num = Column(Integer)
    torrent_size = Column(String(20))


class TorrentFull(Base):
    __tablename__ = 'torrent_update'
    id = Column(Integer, primary_key=True)
    torrent_id = Column(Integer)
    torrent_name = Column(Text)
    torrent_link = Column(String(100))
    torrent_size = Column(String(20))
    torrent_download_link = Column(String(100))
    torrent_up_num = Column(Integer)
    torrent_down_num = Column(Integer)
    create_time = Column(DateTime, default=datetime.now())
    modify_time = Column(DateTime, default=datetime.now())
    free_status = Column(Integer, default=0)
    limit_status = Column(Integer, default=0)
    notify_level = Column(Integer, default=0)
    push_status = Column(Integer, default=0)
