"""
This is a detailed example using almost every command of the API
"""
import requests
import telebot
from telebot import types
import time

from bot.constants import cookie_prefix
from bot.db.dao import query_user, add_user, update_user_cookie, del_torrent_simple_all, add_torrent_simple, \
    query_torrent_simple_by_page
from bot.db.models import User
from bot.spider.bt_spider import get_torrent_simple
from bot.utils import get_vcode_img, get_cookie, DBScheduler, format_torrent_simple_to_msg

TOKEN = "751771463:AAFdkZOYHDw-JACNo8tYb0oCeTZdtZmMavY"

knownUsers = []  # todo: save these in a file,
userStep = {}  # so they won't reset every time the bot restarts

commands = {  # command description used in the "help" command
    'start': 'Get used to the bot',
    'help': 'Gives you information about the available commands',
    'sendLongText': 'A test using the \'send_chat_action\' command',
    'getImage': 'A test using multi-stage messages, custom keyboard, and media sending'
}

user_dict = {}


class User_temp:
    def __init__(self, name, chat_id):
        self.username = name
        self.chat_id = chat_id
        self.password = None
        self.cookie = None


imageSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True)  # create the image selection keyboard
imageSelect.add('cock', 'pussy')

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard


def add_torrent_page_50():
    del_torrent_simple_all()
    for t in get_torrent_simple(50):
        add_torrent_simple(t)


scheduler = DBScheduler(add_torrent_page_50)


# error handling if user isn't known yet
# (obsolete once known users are saved to file, because all users
#   had to use the /start command and are therefore known to the bot)
def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)  # register listener


# handle the "/start" command
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
        bot.send_message(cid, "Hello, stranger, let me scan you...")
        bot.send_message(cid, "Scanning complete, I know you now")
        command_help(m)  # show the new user the help page
    else:
        bot.send_message(cid, "I already know you, no need for me to scan you again!")


# help page
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "The following commands are available: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page


# chat_action example (not a good one...)
@bot.message_handler(commands=['sendLongText'])
def command_long_text(m):
    cid = m.chat.id
    bot.send_message(cid, "If you think so...")
    bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
    time.sleep(3)
    bot.send_message(cid, ".")


# user can chose an image (multi-stage command example)
@bot.message_handler(commands=['getImage'])
def command_image(m):
    cid = m.chat.id
    bot.send_message(cid, "Please choose your image now", reply_markup=imageSelect)  # show the keyboard
    userStep[cid] = 1  # set the user to the next step (expecting a reply in the listener now)


# if the user has issued the "/getImage" command, process the answer
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def msg_image_select(m):
    cid = m.chat.id
    text = m.text

    # for some reason the 'upload_photo' status isn't quite working (doesn't show at all)
    bot.send_chat_action(cid, 'typing')

    if text == "cock":  # send the appropriate image based on the reply to the "/getImage" command
        bot.send_photo(cid, open('rooster.jpg', 'rb'),
                       reply_markup=hideBoard)  # send file and hide keyboard, after image is sent
        userStep[cid] = 0  # reset the users step back to 0
    elif text == "pussy":
        bot.send_photo(cid, open('kitten.jpg', 'rb'), reply_markup=hideBoard)
        userStep[cid] = 0
    else:
        bot.send_message(cid, "Don't type bullsh*t, if I give you a predefined keyboard!")
        bot.send_message(cid, "Please try again")


# filter on a specific message
@bot.message_handler(func=lambda message: message.text == "hi")
def command_text_hi(m):
    bot.send_message(m.chat.id, "I love you too!")


# # default handler for every other text
# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def command_default(m):
#     # this is the standard reply to a normal message
#     bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")


# Handle '/set'
@bot.message_handler(commands=['set'])
def set_user_profile(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Please enter your BYRBT username')
    bot.register_next_step_handler(msg, process_username_step)


def process_username_step(message):
    chat_id = message.chat.id
    try:
        name = message.text
        user = User_temp(name, chat_id)
        user_dict[chat_id] = user
        msg = bot.send_message(chat_id, 'Okay~')
        bot.send_chat_action(chat_id, 'typing')  # show the bot "typing" (max. 5 secs)
        time.sleep(0.5)
        msg = bot.send_message(chat_id,
                               'Now, please enter your BYRBT password\n' +
                               '(we will not store this, the info we will store is only the Cookie)')
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
    try:
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
            bot.send_message(chat_id, 'cookie:\n' + cookie)

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

    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


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
            msg = bot.send_message(chat_id, 'Which page do you want?')
            bot.register_next_step_handler(msg, process_page_num)
        else:
            page_num_str = message.text.replace('/page', '').strip()
            if not page_num_str.isdigit():
                bot.send_message(chat_id, 'Please enter a NUMBER(don\'t more than 50). e.g. /page 1')
                return
            else:
                page_num = int(page_num_str)
                if page_num <= 0 or page_num > 50:
                    bot.send_message(chat_id, 'Page number out of range, please enter a number between 1 to 50.')
                    return
                # TODO: get torrents title and href from database
                torrent_iter = query_torrent_simple_by_page(page_num - 1)
                msg_torrent_page = format_torrent_simple_to_msg(torrent_iter)
                bot.send_message(chat_id, msg_torrent_page, parse_mode='HTML')
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


def process_page_num(message):
    chat_id = message.chat.id
    text = message.text.strip()
    try:
        page_num_str = text
        if not page_num_str.isdigit():
            bot.send_message(chat_id, 'Please enter a NUMBER(don\'t more than 50). e.g. /page 1')
            return
        else:
            page_num = int(page_num_str)
    except Exception as e:
        bot.send_message(chat_id, 'oooops:' + str(e))


# Handle '/test'
@bot.message_handler(commands=['test'])
def command_page(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, '', parse_mode='HTML')


# bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()
# scheduler.start_all()
bot.polling()
