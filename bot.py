# -*- coding: utf-8 -*-
import telebot
import logging
from decouple import config
from time import time, asctime, sleep
from telebot.apihelper import ApiException
import random
import json
import requests
from os import environ

debug_mode = config('DEBUG', cast=bool)
if(debug_mode):
    logging.basicConfig(level=logging.DEBUG)

bot = telebot.TeleBot(config('TELEGRAM_TOKEN'))
headers = {'Authorization': 'Client-ID {}'.format(config('IMGUR_ID'))}

help_text = '''
I will upload any image to imgur.
That's all.
Author: @Pekatarina
Source code: https://github.com/sanguchi/telegram-imgur-bot
'''


@bot.message_handler(content_types=['photo'])
def upload_to_imgur(m):
  photo = m.photo[-1] or m.reply_to_message.photo
  print('photo', photo)
  # print('photo', photo, photo[-1], photo.file_id, photo[-1].file_id)
  file_info = bot.get_file(photo.file_id)
  print('file_info', file_info)
  tg_link = 'https://api.telegram.org/file/bot%s/%s' % (config("TELEGRAM_TOKEN"), file_info.file_path)
  print('tg_link', tg_link)
  res = requests.post('https://api.imgur.com/3/image', headers=headers, data={'image': tg_link})
  if(res.status_code == 200):
    print("User limit: ", res.headers['X-Post-Rate-Limit-Remaining'])
    print("imgur link: ", res.json()['data']['link'])
    bot.reply_to(m, res.json()['data']['link'], disable_web_page_preview=True)
  else:
    bot.reply_to(m, 'Error: You are uploading too fast. Please wait 6 minutes.')
    print('Error:', res)
    # print(res.text, res.headers)

#Help message.
@bot.message_handler(commands=['start', 'help', 'about'])
def help(m):
    bot.reply_to(m, help_text, parse_mode="Markdown")

#Bot starts here.
print('Bot started.')
print('Bot username:[%s]' % bot.get_me().username)

# This makes the bot unstoppable :^)
def safepolling():
    if(bot.skip_pending):
        last_update_id = bot.get_updates()[-1].update_id
    else:
        last_update_id = 0
    while(1):
        logging.debug("Getting updates using update id %s", last_update_id)
        try:
            updates = bot.get_updates(last_update_id + 1, 50)
            logging.debug('Fetched %s updates', len(updates))
            if(len(updates) > 0):
                last_update_id = updates[-1].update_id
                bot.process_new_updates(updates)
        except ApiException as api_exception:
            logging.warning(api_exception)
        except Exception as exception_instance:
            logging.warning(exception_instance)

if(__name__ == '__main__'):
    # Tell owner the bot has started.
    bot.remove_webhook()
    if(debug_mode):
        try:
            bot.send_message(config('OWNER_ID'), 'Bot Started')
        except ApiException:
            logging.critical('''Make sure you have started your bot https://telegram.me/%s.
                And configured the owner variable.''' % bot_info.username)
            exit(1)
    logging.info('Safepolling Start.')
    safepolling()
# Nothing beyond this line will be executed.
