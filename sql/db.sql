CREATE TABLE IF NOT EXISTS `user`(
   `id` int unsigned AUTO_INCREMENT,
   `tg_user_id` int unsigned NOT NULL UNIQUE,
   `bt_user` varchar(20) NOT NULL,
   `bt_cookie` text,
   `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
   `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   `notify_level` int DEFAULT 0,
   `stream_status` int DEFAULT 0,
   `comm_num`      int NOT NULL DEFAULT 0,
   PRIMARY KEY ( `id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `torrent_page_50`(
   `id` int unsigned AUTO_INCREMENT,
   `torrent_id` int unsigned NOT NULL UNIQUE,
   `torrent_name` text NOT NULL,
   `torrent_link` varchar(100) NOT NULL,
   `page` int unsigned,
   `torrent_download_link` varchar(100) NOT NULL,
   `torrent_up_num` int NOT NULL,
   `torrent_down_num` int NOT NULL,
   PRIMARY KEY ( `id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `torrent_update`(
   `id` int unsigned AUTO_INCREMENT,
   `torrent_id` int unsigned NOT NULL UNIQUE,
   `torrent_name` text NOT NULL,
   `torrent_link` varchar(100) NOT NULL,
   `torrent_size` varchar(20) NOT NULL,
   `torrent_download_link` varchar(100) NOT NULL,
   `torrent_up_num` int NOT NULL,
   `torrent_down_num` int NOT NULL,
   `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
   `modify_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   `free_status` int NOT NULL DEFAULT 0,
   `limit_status` int NOT NULL DEFAULT 0,
   `notify_level` int NOT NULL DEFAULT 0,
   `push_status` int NOT NULL DEFAULT 0,
   PRIMARY KEY ( `id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;