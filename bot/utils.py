import configparser
import gzip
import logging
import shutil
import zlib

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from lxml import etree

from bot.constants import url_login, url_base, vcode_save_path, url_takelogin, cookie_prefix, header, torrent_save_path
from bot.log_util import get_logger

logger = get_logger(name='util', level=logging.INFO)


def download_vcode_file(session, link, path, format):
    vcode_hash = link.split('=')[-1]
    file_name = vcode_hash
    return download_file(session=session, header=None, link=link, file_name=file_name, path=path, format=format)


def download_file(session, header, link, file_name, path, format):
    file_type = format if format.startswith('.') else '.' + format
    file_full_name = file_name + file_type
    out_file_path = path + file_full_name if path[-1] == '/' else path + '/' + file_full_name
    # print(link)
    # print(out_file_path)
    if session is not None:
        response = session.get(link, stream=True)
    elif header is not None:
        response = requests.get(link, stream=True, headers=header)
    else:
        raise Exception('download file error')
    if response.headers.get('content-encoding') == 'gzip':
        data = gzip.GzipFile(fileobj=response.raw)
    else:
        data = response.raw
    with open(out_file_path, 'wb') as out_file:
        # print(out_file)
        shutil.copyfileobj(data, out_file)
    return out_file_path, file_name


def get_vcode_img(session):
    response = session.get(url_login)
    html = etree.HTML(response.content)
    vcode_img_src = html.xpath(
        "//td[@id='nav_block']/form[@action='takelogin.php']/table/tr[3]/td[@align='left']/img/@src")
    vcode_img_link = url_base + vcode_img_src[0]
    file_path, vcode_hash = download_vcode_file(session=session, link=vcode_img_link, path=vcode_save_path,
                                                format='.png')
    return file_path, vcode_hash


def get_cookie(session, username, password, vcode, vcode_hash):
    data = {}
    data['username'] = username
    data['password'] = password
    data['imagestring'] = vcode
    data['imagehash'] = vcode_hash
    response = session.post(url_takelogin, data=data)
    cookie_dict = session.cookies.get_dict()
    cookie_str = '; '.join([k + '=' + v for k, v in cookie_dict.items()])
    cookie = cookie_prefix + cookie_str
    return cookie


def convert_size_list(size_raw):
    try:
        if len(size_raw) == 2:
            size_num = float(size_raw[0].strip())
            size_unit = size_raw[1].strip().upper()
            if size_unit == 'GB':
                factor = 1024
            elif size_unit == 'TB':
                factor = 1024 * 1024
            elif size_unit == 'PB':
                factor = 1024 * 1024 * 1024
            elif size_unit == 'MB':
                factor = 1
            else:
                return -1
            return size_num * factor
        else:
            return -1
    except Exception as e:
        return -1


def format_torrent_simple_to_msg(torrent_iter):
    a_tmpl = '<b>{}. </b><a href="{}">{}</a>\n'
    a_list = []
    for i, t in enumerate(torrent_iter):
        t_name = t[1]
        t_name = '{}...'.format(t_name[:50]) if len(t_name) > 50 else t_name
        a_list.append(a_tmpl.format(i + 1, t[2], t_name))
    return ''.join(a_list)


def format_torrent_obj_to_msg(torrent):
    name = torrent.torrent_name
    down_num = torrent.torrent_down_num
    up_num = torrent.torrent_up_num
    size = torrent.torrent_size
    torrent_msg = '{}\n\U00002B07\U0000FE0Fdown: {}\n\U00002B06\U0000FE0Fup: {}\n\U0001F5C4\U0000FE0Fsize: {}\n' \
        .format(name, down_num, up_num, size)
    return torrent_msg


def format_user_info_to_msg(name, upload, download, share_rate, rank):
    user_info_msg = 'User Name: {}\n\U00002B06\U0000FE0F Upload: {}\n\U00002B07\U0000FE0F Download: {}\n\U0001F4CA Share Rate: {}\n\U0001F3C5 Full Rank: {}' \
        .format(name, upload, download, share_rate, rank)
    return user_info_msg


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton(*args):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class BTConfigParser:
    def __init__(self, conf_path='./conf/bt.conf'):
        self.__cf = configparser.RawConfigParser()
        self.__cf.read_file(open(conf_path))
        self.db_url = self.__cf.get('db', 'db_url')
        self.db_port = self.__cf.get('db', 'db_port')
        self.db_user = self.__cf.get('db', 'db_user')
        self.db_password = self.__cf.get('db', 'db_password')
        self.db_database = self.__cf.get('db', 'db_database')
        self.bt_cookie = self.__cf.get('bt', 'bt_cookie')


@singleton
class DBScheduler:
    def __init__(self):
        self.__job_count = 0
        self.__started = False
        self.__scheduler = BackgroundScheduler()

    def add_interval_job(self, func, seconds):
        self.__scheduler.add_job(func, 'interval', seconds=seconds, id='job#{}'.format(self.__job_count))
        self.__job_count += 1

    def start_all(self):
        if not self.__started:
            self.__scheduler.start()
            self.__started = True
            logger.info('scheduler started!')
            return
        else:
            logger.warning('scheduler is running!')
            pass

    def stop_all(self):
        if self.__started:
            self.__scheduler.shutdown()
            self.__started = False
            logger.info('scheduler stopped!')
        else:
            logger.warning('scheduler is not running!')
            pass


if __name__ == '__main__':
    pass
