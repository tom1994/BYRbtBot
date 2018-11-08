from bot.db.models import User, TorrentSimple, TorrentFull
from bot.db.util import session_scope, DBSession


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


# del user
def del_user(tg_user_id):
    with session_scope(DBSession) as session:
        result = session.query(User) \
            .filter(User.tg_user_id == tg_user_id) \
            .first()
        if result is not None:
            session.delete(result)


# query user
def query_user(tg_user_id):
    with session_scope(DBSession) as session:
        result = session.query(User) \
            .filter(User.tg_user_id == tg_user_id) \
            .first()
        return result


# query notify list from user table
def query_notify_list(notify_level):
    with session_scope(DBSession) as session:
        result = session.query(User.tg_user_id) \
            .filter(User.notify_level == notify_level) \
            .all()
        return result


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


# add torrent full to db
def add_torrent_full(torrent):
    with session_scope(DBSession) as session:
        result = session.query(TorrentFull) \
            .filter(TorrentFull.torrent_id == torrent.torrent_id) \
            .first()
        if result is None:
            session.add(torrent)
        else:
            session.merge(torrent)


# query torrent from table torrent_update
def query_torrent_by_notify_level(notify_level):
    with session_scope(DBSession) as session:
        result_raw = session.query(TorrentFull.torrent_id) \
            .filter(TorrentFull.notify_level == notify_level) \
            .all()
        result = [r[0] for r in result_raw]
        return result


# update torrent push status when push complete
def update_torrent_push_status(torrent_id):
    with session_scope(DBSession) as session:
        session.query(TorrentFull) \
            .filter(TorrentFull.torrent_id == torrent_id) \
            .update({TorrentFull.push_status: 1})


if __name__ == '__main__':
    # update_user_cookie(123, 'tomxie', 'hahahahah')
    torrent_list = query_torrent_simple_by_page(0)
    for i, t in enumerate(torrent_list):
        print(i)
        print(t[1])
