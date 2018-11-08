import configparser
import shutil

from lxml import etree

from bot.constants import url_login, url_base, vcode_save_path, url_takelogin, cookie_prefix


def download_file(session, link, path, format):
    vcode_hash = link.split('=')[-1]
    file_type = format if format.startswith('.') else '.' + format
    file_name = vcode_hash + file_type
    out_file_path = path + file_name if path[-1] == '/' else path + '/' + file_name
    # print(link)
    # print(out_file_path)
    response = session.get(link, stream=True)
    with open(out_file_path, 'wb') as out_file:
        # print(out_file)
        shutil.copyfileobj(response.raw, out_file)
    return out_file_path, vcode_hash


def get_vcode_img(session):
    response = session.get(url_login)
    html = etree.HTML(response.content)
    vcode_img_src = html.xpath(
        "//td[@id='nav_block']/form[@action='takelogin.php']/table/tr[3]/td[@align='left']/img/@src")
    vcode_img_link = url_base + vcode_img_src[0]
    file_path, vcode_hash = download_file(session, vcode_img_link, vcode_save_path, '.png')
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


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton(*args):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class BTConfigParser:
    def __init__(self, conf_path='conf/bt.conf'):
        self.__cf = configparser.RawConfigParser()
        self.__cf.read_file(open(conf_path))
        self.db_url = self.__cf.get('db', 'db_url')
        self.db_port = self.__cf.get('db', 'db_port')
        self.db_user = self.__cf.get('db', 'db_user')
        self.db_password = self.__cf.get('db', 'db_password')
        self.db_database = self.__cf.get('db', 'db_database')
        self.bt_cookie = self.__cf.get('bt', 'bt_cookie')


if __name__ == '__main__':
    print(BTConfigParser().bt_cookie)
