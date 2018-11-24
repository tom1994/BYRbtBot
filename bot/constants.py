url_login = 'https://bt.byr.cn/login.php'
url_takelogin = 'https://bt.byr.cn/takelogin.php'
url_base = 'https://bt.byr.cn/'
url_index = 'https://bt.byr.cn/index.php'
url_torrents = 'https://bt.byr.cn/torrents.php?inclbookmarked=0&incldead=0&spstate=0&page={}'
url_download_prefix = "https://bt.byr.cn/"
vcode_save_path = '../vcode_img'
torrent_save_path = '../torrents'
cookie_prefix = 'byrbta4=1; _ga=GA1.2.1546056671.1512354848; byrbta3=0; byrbta=0; byrbta2=0; byrbta1=0; _gid=GA1.2.1475180723.1540050390; _gat=1; '
header = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "",
    "dnt": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}
page_50_interval = 300  # second

expire_time = 60  # day

cat_map = {
    '?cat=408': ('\U0001F39E\U0000FE0FMovie', '\U0001F39E\U0000FE0F'),
    '?cat=401': ('\U0001F4FATV series', '\U0001F4FA'),
    '?cat=404': ('\U0001F431Anime', '\U0001F431'),
    '?cat=402': ('\U0001F3B5Music', '\U0001F3B5'),
    '?cat=405': ('\U0001F37FVariety', '\U0001F37F'),
    '?cat=403': ('\U0001F3AEGame', '\U0001F3AE'),
    '?cat=406': ('\U0001F4BFSoftware', '\U0001F4BF'),
    '?cat=407': ('\U0001F4C3Document', '\U0001F4C3'),
    '?cat=409': ('\U000026BDSports', '\U000026BD'),
    '?cat=410': ('\U0001F30EDocumentary', '\U0001F30E'),
    'other': ('\U0001F914Other', '\U0001F914')
}
