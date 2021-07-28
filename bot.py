#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from dotenv import dotenv_values
import os, requests, json, uuid
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))

#Get variables from .env file.
config = dotenv_values(".env")

bot_token = config['BOT_TOKEN']
azure_key = config['AZURE_KEY']
azure_endpoint = config['AZURE_ENDPOINT']
location = config['LOCATION']


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def translate(update, context):
    """Translate user message. It has to have the following format:
        message >lang. Example 'hello >es' """
    [text, language] = update.message.text.split(">")
    logger.info('"%s", "%s"', text, language)
    path = '/translate?api-version=3.0'
    target_language_parameter = '&to=' + language
    constructed_url = azure_endpoint + path + target_language_parameter

    headers = {
        'Ocp-Apim-Subscription-Key': azure_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{ 'text': text }]

    #make request to Azure translator API.
    translator_request = requests.post(constructed_url, headers=headers, json=body)
    translator_response = translator_request.json()
    translated_text = translator_response[0]['translations'][0]['text']
    print("Translated text: ", translated_text)
    
    #return translation to user.
    update.message.reply_text(translated_text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    print("jelo")
    updater = Updater(bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_handler(MessageHandler(Filters.text, translate))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    #updater.start_polling()

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=bot_token)
                          #webhook_url="https://emitrbot.herokuapp.com/" + TOKEN)
    updater.bot.set_webhook("https://emitrbot.herokuapp.com/" + bot_token)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    
    main()