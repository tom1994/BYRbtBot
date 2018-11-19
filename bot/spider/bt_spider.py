import logging
import re
import time

import requests
from lxml import etree
from bot.constants import url_login, url_base, vcode_save_path, url_takelogin, cookie_prefix, url_torrents, \
    url_download_prefix, header, url_index
from bot.db.dao import del_torrent_simple_all, add_torrent_simple, add_torrent_full
from bot.db.models import TorrentSimple, TorrentFull
from bot.log_util import get_logger
from bot.utils import download_file, BTConfigParser, format_user_info_to_msg

cookie = BTConfigParser().bt_cookie
spider_header = dict(header)
spider_header['cookie'] = cookie
logger = get_logger(name='bt_spider', level=logging.INFO)


class Torrent:
    def __init__(self, id, name, link, size, download_link, up_num, down_num, free_status, limit_status, page):
        self.id = id
        self.name = name
        self.link = link
        self.size = size
        self.download_link = download_link
        self.up_num = up_num
        self.down_num = down_num
        self.free_status = free_status
        self.limit_status = limit_status
        self.page = page

    def to_torrent_obj_full(self):
        torrent_obj = TorrentFull()
        torrent_obj.torrent_id = self.id
        torrent_obj.torrent_name = self.name
        torrent_obj.torrent_link = self.link
        torrent_obj.torrent_size = self.size
        torrent_obj.torrent_download_link = self.download_link
        torrent_obj.torrent_up_num = self.up_num
        torrent_obj.torrent_down_num = self.down_num
        torrent_obj.free_status = self.free_status
        torrent_obj.limit_status = self.limit_status
        if self.free_status == 1 and (
                self.limit_status == 1 or (0 < self.up_num < 5 and self.down_num / self.up_num > 7)):
            torrent_obj.notify_level = 3
        elif self.free_status == 1:
            torrent_obj.notify_level = 2
        else:
            torrent_obj.notify_level = 1
        return torrent_obj

    def to_torrent_obj_lite(self):
        torrent_obj = TorrentSimple()
        torrent_obj.torrent_id = self.id
        torrent_obj.torrent_name = self.name
        torrent_obj.torrent_link = self.link
        torrent_obj.page = self.page
        torrent_obj.torrent_download_link = self.download_link
        torrent_obj.torrent_up_num = self.up_num
        torrent_obj.torrent_down_num = self.down_num
        torrent_obj.torrent_size = self.size
        return torrent_obj


def get_torrents_by_page(page):
    response = requests.get(url=url_torrents.format(page), headers=spider_header)
    html = etree.HTML(response.content)
    all_torrents = html.xpath("//table[@class='torrents']/form[@id='form_torrent']/tr")
    torrent_list = []
    for torrent in all_torrents:
        torrent_name = torrent.xpath(".//table[@class='torrentname']//tr/td[1]/a/@title")
        # remove table title
        if len(torrent_name) == 0:
            continue
        free_flag = len(torrent.xpath(
            ".//table[@class='torrentname']//tr[@class='free_bg' or @class='twoupfree_bg']/td[1]/a/@title"))
        free_status = 1 if free_flag > 0 else 0
        torrent_link = url_base + torrent.xpath(".//table[@class='torrentname']//tr/td[1]/a/@href")[0]
        torrent_download_link = url_download_prefix + \
                                torrent.xpath(".//table[@class='torrentname']//td[@width='20']/a[1]/@href")[0]
        # get torrent id
        torrent_id = re.search(r'\?id=(\d+)', torrent_download_link).group(1)
        # three types of upload number
        upload_num1 = torrent.xpath("./td[@align='center' and @class='rowfollow']/b/a/text()")
        upload_num2 = torrent.xpath("./td[@class='rowfollow']/span[@class='red']/text()")
        upload_num3 = torrent.xpath("./td[@align='center' and @class='rowfollow']/b/a/font/text()")
        upload_num_list = upload_num1 or upload_num2 or upload_num3
        upload_num = int(re.sub(r'\W+', '', upload_num_list[0]))
        # if this torrent is limited
        limit_status = 1 if len(upload_num3) != 0 else 0
        # two types of download number
        download_num1 = torrent.xpath("./td[@class='rowfollow'][5]/b/a/text()")
        download_num2 = torrent.xpath("./td[@class='rowfollow'][5]/text()")
        download_num_list = download_num1 or download_num2
        download_num = int(re.sub(r'\W+', '', download_num_list[0]))
        # get torrent size list [num, unit]
        torrent_size_raw = torrent.xpath("./td[@class='rowfollow'][3]/text()")
        torrent_size = ''.join(torrent_size_raw)

        t = Torrent(id=torrent_id, name=torrent_name[0], link=torrent_link, size=torrent_size,
                    download_link=torrent_download_link, up_num=upload_num, down_num=download_num,
                    free_status=free_status, limit_status=limit_status, page=page)
        yield t


def get_torrent_simple(max):
    for i in range(max):
        torrent_list_i = get_torrents_by_page(i)
        # torrent_list.extend([t.to_torrent_obj_lite() for t in torrent_list_i])
        for t in torrent_list_i:
            yield t.to_torrent_obj_lite()


def get_torrent_full(max):
    for i in range(max):
        torrent_list_i = get_torrents_by_page(i)
        for t in torrent_list_i:
            yield t.to_torrent_obj_full()


def get_user_info(cookie):
    user_header = dict(header)
    user_header['cookie'] = cookie
    response = requests.get(url=url_index, headers=user_header)
    html = etree.HTML(response.content)
    user_info_box = html.xpath("//table[@id='info_block']//table/tr/td[@align='left']/span[@class='medium']")[0]
    user_name_text = user_info_box.xpath("./span[@class='nowrap']/a/b/text()")
    user_info_text = user_info_box.xpath("./text()")
    user_name = user_name_text[0].strip()
    share_rate = user_info_text[10].strip()
    upload = user_info_text[11].strip()
    download = user_info_text[12].strip()
    user_info_msg = format_user_info_to_msg(name=user_name, upload=upload, download=download, share_rate=share_rate)
    return user_info_msg


if __name__ == '__main__':
    # for t in get_torrent_full(1):
    #     add_torrent_full(t)
    # logger.info('tic')
    # try:
    #     del_torrent_simple_all()
    #     for t in get_torrent_simple(20):
    #         add_torrent_simple(t)
    #         time.sleep(0.1)
    # except Exception as e:
    #     logger.error(str(e))
    # logger.info('toc')
    cookie = '*****'
    # cookie = cookie_prefix + cookie
    print(get_user_info(cookie))
