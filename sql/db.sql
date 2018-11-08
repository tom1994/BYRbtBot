CREATE TABLE IF NOT EXISTS `user`(
   `id` int unsigned AUTO_INCREMENT,
   `tg_user_id` int unsigned NOT NULL UNIQUE,
   `bt_user` varchar(20) NOT NULL,
   `bt_cookie` text,
   `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
   `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   `notify_level` int DEFAULT 0,
   PRIMARY KEY ( `id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `torrent_page_50`(
   `id` int unsigned AUTO_INCREMENT,
   `torrent_id` int unsigned NOT NULL UNIQUE,
   `torrent_name` varchar(100) NOT NULL,
   `torrent_link` varchar(100) NOT NULL,
   `page` int unsigned,
   PRIMARY KEY ( `id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;