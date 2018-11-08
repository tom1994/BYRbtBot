import re
import requests
from lxml import etree
from bot.constants import url_login, url_base, vcode_save_path, url_takelogin, cookie_prefix, url_torrents, \
    url_download_prefix
from bot.db.dao import del_torrent_simple_all, add_torrent_simple
from bot.db.models import TorrentSimple, TorrentFull
from bot.utils import download_file, BTConfigParser

cookie = BTConfigParser().bt_cookie
header = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "cookie": cookie,
    "dnt": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}


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
        # todo: add convert function to torrent db obj
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
        return torrent_obj


def get_torrents_by_page(page):
    response = requests.get(url=url_torrents.format(page), headers=header)
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
        upload_num = upload_num_list[0]
        # if this torrent is limited
        limit_status = 1 if len(upload_num3) != 0 else 0
        # two types of download number
        download_num1 = torrent.xpath("./td[@class='rowfollow'][5]/b/a/text()")
        download_num2 = torrent.xpath("./td[@class='rowfollow'][5]/text()")
        download_num_list = download_num1 or download_num2
        download_num = download_num_list[0]
        # get torrent size list [num, unit]
        torrent_size_raw = torrent.xpath("./td[@class='rowfollow'][3]/text()")
        torrent_size = ''.join(torrent_size_raw)

        # print(torrent_name[0])
        # print(free_status)
        # print(limit_status)
        # print(torrent_link)
        # print(torrent_download_link)
        # print(torrent_id)
        # print(upload_num)
        # print(download_num)
        # print(torrent_size)
        t = Torrent(id=torrent_id, name=torrent_name[0], link=torrent_link, size=torrent_size,
                    download_link=torrent_download_link, up_num=upload_num, down_num=download_num,
                    free_status=free_status, limit_status=limit_status, page=page)
        # torrent_list.append(t)
        yield t
    # print(len(torrent_list))
    # return torrent_list


def get_torrent_simple(max):
    torrent_list = []
    for i in range(max):
        torrent_list_i = get_torrents_by_page(i)
        # torrent_list.extend([t.to_torrent_obj_lite() for t in torrent_list_i])
        for t in torrent_list_i:
            yield t.to_torrent_obj_lite()
    # return torrent_list


if __name__ == '__main__':
    del_torrent_simple_all()
    for t in get_torrent_simple(50):
        add_torrent_simple(t)
