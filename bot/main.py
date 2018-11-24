"""
This is a detailed example using almost every command of the API
"""
import logging
import re

import requests
import telebot
from telebot import types
import time

from bot.constants import cookie_prefix, header, torrent_save_path, cat_map
from bot.db.dao import query_user, add_user, update_user_cookie, del_torrent_simple_all, add_torrent_simple, \
    query_torrent_simple_by_page, update_user_notify_level, add_torrent_full, query_user_by_notify_level, \
    query_torrent_id_by_notify_level, query_torrent_by_id, update_torrent_push_status, query_user_lower_notify_level, \
    update_user_stream_status, query_torrent_simple_by_page_order, update_user_comm_num
from bot.db.models import User
from bot.log_util import get_logger
from bot.spider.bt_spider import get_torrent_simple, get_torrent_full, get_user_info
from bot.utils import get_vcode_img, get_cookie, DBScheduler, format_torrent_simple_to_msg, format_torrent_obj_to_msg, \
    download_file

TOKEN = "751771463:AAFdkZOYHDw-JACNo8tYb0oCeTZdtZmMavY"

logger = get_logger(name='main', level=logging.INFO)

commands = {  # command description used in the "help" command
    'start': 'Start used to the bot',
    'help': 'Give you information about the available commands',
    'page': 'Explore the BYRBT torrents in a page',
    'set': 'Set your BYRBT account',
    'set_notify_level': 'Set your notify level',
    'info': 'Get BYRBT user info',
    'start_stream': 'Start torrents pushing',
    'stop_stream': 'Stop torrents pushing'
}

user_dict = {}


class UserTemp:
    def __init__(self, name, chat_id):
        self.username = name
        self.chat_id = chat_id
        self.password = None
        self.cookie = None


# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            chat_id = m.chat.id
            # print the sent message to the console
            logger.info(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)
            # print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)
            # auto increment comm number
            update_user_comm_num(chat_id)


bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)  # register listener


def create_torrent_makeup(torrent):
    download_link = torrent.torrent_download_link
    link = torrent.torrent_link
    markup = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton(text=str(u'\U0001F4BE') + " Download", callback_data="d-" + download_link))
    row.append(types.InlineKeyboardButton(text=str(u'\U0001F517') + " Link", url=link))
    markup.row(*row)
    return markup


def create_page_makeup(page_name):
    markup = types.InlineKeyboardMarkup()
    row = []
    row.append(
        types.InlineKeyboardButton(text=str(u'\U0001F4BE') + " Download",
                                   callback_data='p-{}'.format(str(page_name))))
    markup.row(*row)
    return markup


def add_torrent_page_n():
    try:
        del_torrent_simple_all()
        for t in get_torrent_simple(10):
            add_torrent_simple(t)
            time.sleep(0.1)
    except Exception as e:
        logger.error(str(e))


def update_torrent_stream():
    try:
        for t in get_torrent_full(1):
            add_torrent_full(t)
    except Exception as e:
        logger.error(str(e))


def push_torrent_stream():
    try:
        notify_level_list = [1, 2, 3]
        for n in notify_level_list:
            torrent_id_list = query_torrent_id_by_notify_level(n)
            user_c_time_list = query_user_lower_notify_level(n)
            logger.info(
                'get torrents in notify level {} list: {}'.format(str(n), ','.join([str(t) for t in torrent_id_list])))
            logger.info(
                'get users in notify level {} list: {}'.format(str(n), ','.join([str(u[0]) for u in user_c_time_list])))
            for t_id in torrent_id_list:
                torrent = query_torrent_by_id(t_id)
                torrent_msg = format_torrent_obj_to_msg(torrent)
                torrent_makeup = create_torrent_makeup(torrent)
                torrent_create_time = torrent.create_time
                for u_id, c_time in user_c_time_list:
                    if c_time < torrent_create_time:
                        bot.send_message(u_id, torrent_msg, parse_mode='HTML', reply_markup=torrent_makeup)
                        logger.info('pushed torrent {} to user {}'.format(str(t_id), str(u_id)))
                update_torrent_push_status(t_id, n)
                logger.info('torrent {} status in notify level {} updated'.format(str(t_id), str(n)))
    except Exception as e:
        logger.error(str(e))


# def test_push():
#     chat_id = 137802064
#     bot.send_message(chat_id, 'hello')


scheduler = DBScheduler()

scheduler.add_interval_job(add_torrent_page_n, seconds=300)
scheduler.add_interval_job(update_torrent_stream, seconds=30)
scheduler.add_interval_job(push_torrent_stream, seconds=120)


# scheduler.add_interval_job(test_push, seconds=5)


# error handling if user isn't known yet
# (obsolete once known users are saved to file, because all users
#   had to use the /start command and are therefore known to the bot)
# def get_user_step(uid):
#     if uid in userStep:
#         return userStep[uid]
#     else:
#         knownUsers.append(uid)
#         userStep[uid] = 0
#         print("New user detected, who hasn't used \"/start\" yet")
#         return 0


# handle the "/start" command
@bot.message_handler(commands=['start'])
def command_start(m):
    chat_id = m.chat.id
    bot.send_message(chat_id, '''Nice to meet you~\n
Now, you can use /page command to explore some torrents.\n
Or, you can use /start_stream command to receive some new update torrents.\n
If you want to download, please use /set command first to set your account.\n
For more information, please use /help command.\n
Enjoy!!!''')


# help page
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "The following commands are available: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page


# filter on a specific message
@bot.message_handler(func=lambda message: message.text == "hi")
def command_text_hi(m):
    bot.send_message(m.chat.id, "Aloha!")


# # default handler for every other text
# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def command_default(m):
#     # this is the standard reply to a normal message
#     bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")


# Handle '/set'
@bot.message_handler(commands=['set'])
def command_set(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Please enter your BYRBT username')
    markup = types.ForceReply(selective=False)
    msg = bot.send_message(chat_id, 'Enter your BYRBT username:', reply_markup=markup)
    bot.register_next_step_handler(msg, process_username_step)


def process_username_step(message):
    chat_id = message.chat.id
    try:
        name = message.text
        user = UserTemp(name, chat_id)
        user_dict[chat_id] = user
        bot.send_message(chat_id, 'Okay~')
        bot.send_chat_action(chat_id, 'typing')  # show the bot "typing" (max. 5 secs)
        time.sleep(0.5)
        bot.send_message(chat_id,
                         'Now, please enter your BYRBT password\n' +
                         '(we will not store this, the info we will store is only the Cookie)')
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(chat_id, 'Enter your BYRBT password:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_password_step)
    except Exception as e:
        bot.send_message(chat_id, 'oooops' + str(e))


def process_password_step(message):
    chat_id = message.chat.id
    msg_id = message.message_id
    try:
        password = message.text
        user = user_dict[chat_id]
        user.password = password
        msg = bot.send_message(chat_id, 'Okay~')
        bot.send_chat_action(chat_id, 'typing')  # show the bot "typing" (max. 5 secs)
        time.sleep(0.2)
        s = requests.Session()
        path, hash = get_vcode_img(s)
        bot.send_message(chat_id, 'Now, please enter the verification code below\n')
        msg = bot.send_photo(chat_id, open(path, 'rb'))
        bot.register_next_step_handler(msg, process_vcode_step, s, hash)
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


def process_vcode_step(message, session, hash):
    chat_id = message.chat.id
    # try:
    vcode_str = message.text
    user = user_dict[chat_id]
    bot.send_message(chat_id, 'Okay~')
    bot.send_chat_action(chat_id, 'typing')  # show the bot "typing" (max. 5 secs)
    time.sleep(0.5)

    cookie = get_cookie(session, user.username, user.password, vcode_str, hash)
    user.cookie = cookie

    if cookie == cookie_prefix:
        bot.send_message(chat_id, 'Get cookie ERROR!')
        return
    else:
        bot.send_message(chat_id, 'Get cookie Success!')
        bot.send_message(chat_id, 'Now, please use /set_notify_level to set your notify level.')

    # save or update user in database
    result = query_user(chat_id)
    if result is None:
        user_obj = User()
        user_obj.tg_user_id = user.chat_id
        user_obj.bt_user = user.username
        user_obj.bt_cookie = user.cookie
        add_user(user_obj)
    else:
        update_user_cookie(user.chat_id, user.username, user.cookie)


# except Exception as e:
#     bot.send_message(chat_id, 'oooops:' + str(e))


# Handle '/page {%d}'
@bot.message_handler(commands=['page'])
def command_page(message):
    chat_id = message.chat.id
    text = message.text.strip()
    try:
        if text == '/page':
            bot.send_message(chat_id, 'Okay~')
            bot.send_chat_action(chat_id, 'typing')  # show the bot "typing" (max. 5 secs)
            time.sleep(0.2)
            msg = bot.send_message(chat_id, 'Which page do you want? [1-10]')
            bot.register_next_step_handler(msg, process_page_num)
        else:
            page_num_str = message.text.replace('/page', '').strip()
            send_torrent_page(chat_id, page_num_str)
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


def process_page_num(message):
    chat_id = message.chat.id
    text = message.text.strip()
    try:
        page_num_str = text
        send_torrent_page(chat_id, page_num_str)
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


def send_torrent_page(chat_id, page_num_str):
    if not page_num_str.isdigit():
        bot.send_message(chat_id, 'Please enter a NUMBER(don\'t more than 10). e.g. /page 1')
        return
    else:
        page_num = int(page_num_str)
        if page_num <= 0 or page_num > 20:
            bot.send_message(chat_id, 'Page number out of range, please enter a number between 1 to 10.')
            return
        torrent_iter = query_torrent_simple_by_page(page_num - 1)
        msg_torrent_page = format_torrent_simple_to_msg(torrent_iter)
        msg_torrent_page = 'Page {}\n'.format(page_num) + msg_torrent_page
        makeup = create_page_makeup(page_num)
        bot.send_message(chat_id, msg_torrent_page, parse_mode='HTML', reply_markup=makeup)


# Handle '/set_notify_level'
@bot.message_handler(commands=['set_notify_level'])
def command_set_notify_level(message):
    chat_id = message.chat.id
    text = message.text.strip()
    try:
        if text == '/set_notify_level':
            bot.send_message(chat_id, 'Okay~')
            bot.send_chat_action(chat_id, 'typing')  # show the bot "typing" (max. 5 secs)
            time.sleep(0.2)
            msg = bot.send_message(chat_id,
                                   'Please enter your notify level~\n1: receive all new update torrents\n' + \
                                   '2: receive all new update free torrents(include free and freeX2)\n' + \
                                   '3: receive new update hot torrents(free and upload limited, if you want to get more upload, PLEASE pick me \U00002764\U0000FE0F)')
            bot.register_next_step_handler(msg, process_notify_level)
        else:
            notify_level_str = message.text.replace('/set_notify_level', '').strip()
            update_notify_level(chat_id, notify_level_str)
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


def process_notify_level(message):
    chat_id = message.chat.id
    text = message.text.strip()
    try:
        notify_level_str = text
        update_notify_level(chat_id, notify_level_str)
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


def update_notify_level(chat_id, notify_level_str):
    if not notify_level_str.isdigit():
        bot.send_message(chat_id, 'Please enter a NUMBER.')
        return
    else:
        notify_level = int(notify_level_str)
        if notify_level <= 0 or notify_level > 3:
            bot.send_message(chat_id, 'Page number out of range, please enter a number in 1 2 and 3.')
            return
        result = query_user(chat_id)
        if result is not None:
            update_user_notify_level(chat_id, notify_level)
            bot.send_message(chat_id, 'Update notify level success. ' +
                             '\nNow, you can use /start_stream to start receive torrent update.')
        else:
            bot.send_message(chat_id, 'Sorry, we didn\'t have your cookie yet. Please use /set to set your cookie.')


# Handle '/start_stream'
@bot.message_handler(commands=['start_stream'])
def command_start_stream(message):
    chat_id = message.chat.id
    try:
        user = query_user(chat_id)
        if user is None:
            bot.send_message(chat_id, 'Please set user information with command /set first.')
        elif user.notify_level == 0:
            bot.send_message(chat_id, 'Please set your notify level with command /set_notify_level .')
        else:
            update_user_stream_status(chat_id, 1)
            bot.send_message(chat_id, 'Stream started! \nUse /stop_stream to stop.')
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


# Handle '/stop_stream'
@bot.message_handler(commands=['stop_stream'])
def command_stop_stream(message):
    chat_id = message.chat.id
    try:
        user = query_user(chat_id)
        if user is None:
            bot.send_message(chat_id, 'Please set user information with command /set first.')
        else:
            update_user_stream_status(chat_id, 0)
            bot.send_message(chat_id, 'Stream stopped.')
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


@bot.callback_query_handler(func=lambda call: call.data.startswith('d-'))
def callback_download_torrent(call):
    chat_id = call.message.chat.id
    try:
        download_link = call.data[2:]
        torrent_id = re.search(r'\?id=(\d+)', download_link).group(1)
        user = query_user(chat_id)
        user_cookie = user.bt_cookie
        user_header = dict(header)
        user_header['cookie'] = user_cookie
        file_name = '_'.join([str(torrent_id), str(chat_id)])
        file_path, _ = download_file(session=None, header=user_header, link=download_link, path=torrent_save_path,
                                     file_name=file_name, format='.torrent')
        torrent_file = open(file_path, 'rb')
        files = {'document': torrent_file}
        response = requests.post("https://api.telegram.org/bot{}/sendDocument?chat_id={}".format(TOKEN, str(chat_id)),
                                 files=files)
        if str(response.status_code) != '200':
            bot.send_message(chat_id, 'Download torrent file fail!')

    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


@bot.callback_query_handler(func=lambda call: call.data.startswith('p-'))
def callback_page_torrent_download(call):
    chat_id = call.message.chat.id
    try:
        result = query_user(chat_id)
        if result is None:
            bot.send_message(chat_id, 'Please set your account with command /set first.')
            return
        page_num_str = call.data[2:]
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(chat_id, 'OK, which one do you want to download? [1-50]', reply_markup=markup)
        bot.register_next_step_handler(msg, process_page_order_reply, page_num_str)
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


def process_page_order_reply(message, page_num_str):
    chat_id = message.chat.id
    order_num_str = message.text
    if not order_num_str.isdigit():
        bot.send_message(chat_id, 'Please enter a NUMBER(don\'t more than 50).')
    else:
        order_num = int(order_num_str)
        page_num = int(page_num_str)
        torrent = query_torrent_simple_by_page_order(page_num - 1, order_num - 1)
        torrent_msg = format_torrent_obj_to_msg(torrent)
        makeup = create_torrent_makeup(torrent)
        bot.send_message(chat_id, torrent_msg, parse_mode='HTML', reply_markup=makeup)


# Handle '/info'
@bot.message_handler(commands=['info'])
def command_info(message):
    chat_id = message.chat.id
    try:
        user = query_user(chat_id)
        if user is None:
            bot.send_message(chat_id, 'Please set your account with command /set first.')
            return
        cookie = user.bt_cookie
        user_info_msg = get_user_info(cookie)
        bot.send_message(chat_id, user_info_msg)
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


# Handle '/test'
@bot.message_handler(commands=['test'])
def command_test(message):
    chat_id = message.chat.id
    cat_list = [v[0] + ',' + v[1] for v in cat_map.values()]
    msg = '\n'.join(cat_list)
    bot.send_message(chat_id, msg)


# bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()
while True:
    try:
        scheduler.start_all()
        bot.polling(none_stop=False)
    except Exception as e:
        time.sleep(5)
        logger.error(str(e))
        bot.stop_polling()
        logger.warning('bot stop polling!')
