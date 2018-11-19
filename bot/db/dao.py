import datetime

from sqlalchemy.sql import operators

from bot.constants import expire_time
from bot.db.models import User, TorrentSimple, TorrentFull
from bot.db.util import session_scope, DBSession


# ------ table user -------
# add user
def add_user(user):
    with session_scope(DBSession) as session:
        result = session.query(User) \
            .filter(user.tg_user_id == User.tg_user_id) \
            .first()
        if result is not None:
            user.id = result.id
            session.merge(user)
        else:
            session.add(user)


# update user cookie
def update_user_cookie(tg_user_id, new_name, new_cookie):
    with session_scope(DBSession) as session:
        session.query(User) \
            .filter(tg_user_id == User.tg_user_id) \
            .update({User.bt_user: new_name,
                     User.bt_cookie: new_cookie})


# update user notify level
def update_user_notify_level(tg_user_id, new_level):
    with session_scope(DBSession) as session:
        session.query(User) \
            .filter(tg_user_id == User.tg_user_id) \
            .update({User.notify_level: new_level})


# update user stream status
def update_user_stream_status(tg_user_id, new_stream_status):
    with session_scope(DBSession) as session:
        session.query(User) \
            .filter(tg_user_id == User.tg_user_id) \
            .update({User.stream_status: new_stream_status})


# update user comm number
def update_user_comm_num(tg_user_id):
    with session_scope(DBSession) as session:
        session.query(User) \
            .filter(tg_user_id == User.tg_user_id) \
            .update({User.comm_num: User.comm_num + 1})


# del user
def del_user(tg_user_id):
    with session_scope(DBSession) as session:
        result = session.query(User) \
            .filter(User.tg_user_id == tg_user_id) \
            .first()
        if result is not None:
            session.delete(result)


# del expire users use modify time
def del_expire_user():
    with session_scope(DBSession) as session:
        now = datetime.datetime.now()
        expire_threshold = now - datetime.timedelta(days=expire_time)
        result = session.query(User) \
            .filter(User.modify_time < expire_threshold) \
            .all()
        for r in result:
            session.delete(r)


# query user
def query_user(tg_user_id):
    with session_scope(DBSession) as session:
        result = session.query(User) \
            .filter(User.tg_user_id == tg_user_id) \
            .first()
        if result is not None:
            session.expunge(result)  # !important
        return result


# query user id list from user table by notify level
def query_user_by_notify_level(notify_level):
    with session_scope(DBSession) as session:
        result = session.query(User.tg_user_id, User.create_time) \
            .filter(User.stream_status == 1) \
            .filter(User.notify_level == notify_level) \
            .all()
        return result


# query user id list from user table which has lower notify level
def query_user_lower_notify_level(notify_level):
    with session_scope(DBSession) as session:
        result = session.query(User.tg_user_id, User.create_time) \
            .filter(User.stream_status == 1) \
            .filter(User.notify_level <= notify_level) \
            .all()
        return result


# ------ table torrent_page_50 -------
# add torrent to db
def add_torrent_simple(torrent):
    with session_scope(DBSession) as session:
        result = session.query(TorrentSimple) \
            .filter(TorrentSimple.torrent_id == torrent.torrent_id) \
            .first()
        if result is None:
            session.add(torrent)


# clean torrent page table
def del_torrent_simple_all():
    with session_scope(DBSession) as session:
        session.query(TorrentSimple).delete()


# get torrent use page
def query_torrent_simple_by_page(page):
    with session_scope(DBSession) as session:
        result = session.query(TorrentSimple.torrent_id, TorrentSimple.torrent_name, TorrentSimple.torrent_link) \
            .filter(TorrentSimple.page == page) \
            .all()
        return result


# get torrent use page and order
def query_torrent_simple_by_page_order(page, order):
    with session_scope(DBSession) as session:
        result = session.query(TorrentSimple) \
            .filter(TorrentSimple.page == page) \
            .limit(1) \
            .offset(order) \
            .first()
        if result is not None:
            session.expunge(result)  # !important
        return result


# ------- table torrent update -------
# add torrent full to db
def add_torrent_full(torrent):
    with session_scope(DBSession) as session:
        result = session.query(TorrentFull) \
            .filter(TorrentFull.torrent_id == torrent.torrent_id) \
            .first()
        if result is None:
            session.add(torrent)
        else:
            torrent.id = result.id
            session.merge(torrent)


# query torrent object use torrent id
def query_torrent_by_id(torrent_id):
    with session_scope(DBSession) as session:
        result = session.query(TorrentFull) \
            .filter(TorrentFull.torrent_id == torrent_id) \
            .first()
        if result is not None:
            session.expunge(result)
        return result


# query torrent from table torrent_update (no push)
def query_torrent_id_by_notify_level(notify_level):
    with session_scope(DBSession) as session:
        result_raw = session.query(TorrentFull.torrent_id) \
            .filter(TorrentFull.notify_level == notify_level)
        if notify_level == 1:
            result_raw = result_raw.filter(operators.op(TorrentFull.push_status, '&', 1) == 0).all()
        elif notify_level == 2:
            result_raw = result_raw.filter(operators.op(TorrentFull.push_status, '&', 2) == 0).all()
        elif notify_level == 3:
            result_raw = result_raw.filter(operators.op(TorrentFull.push_status, '&', 4) == 0).all()
        else:
            result_raw = result_raw.all()
        result = [r[0] for r in result_raw]
        return result


# update torrent push status when push complete
def update_torrent_push_status(torrent_id, notify_level):
    with session_scope(DBSession) as session:
        result_raw = session.query(TorrentFull) \
            .filter(TorrentFull.torrent_id == torrent_id) \
            .filter(TorrentFull.notify_level == notify_level) \
            .all()
        for r in result_raw:
            if notify_level == 1:
                r.push_status = r.push_status | 1
            elif notify_level == 2:
                r.push_status = r.push_status | 2
            elif notify_level == 3:
                r.push_status = r.push_status | 4
            else:
                pass


if __name__ == '__main__':
    # update_user_cookie(123, 'tomxie', 'hahahahah')
    user = query_user(1234)
    print(user)
    # print(query_torrent_id_by_notify_level(2))
    # update_torrent_push_status(272834, 2)
