import telegram
from telegram.ext import CommandHandler, Filters, MessageHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
from telegram.ext import CallbackQueryHandler

from bot_config import dispatcher
import bot_functions


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Sou um bot, por favor, fale comigo!")

def help_command(update, context):
    update.message.reply_text("Digite /start para testar bot.")

def nada(update, context):
    kb = [[telegram.InlineKeyboardButton('nadica', callback_data='1')],
          [telegram.InlineKeyboardButton('quase nada', callback_data='2')],
          [telegram.InlineKeyboardButton('nada mesmo', callback_data='3')]]
    kb_markup = telegram.InlineKeyboardMarkup(kb)
    update.message.reply_text('Choices:', reply_markup=kb_markup)

def button(update, context):
    query = update.callback_query
    query.answer()
    
    if(query.data == '1'):
        context.bot.sendPhoto(chat_id=update.effective_chat.id, 
                              photo="https://telegram.org/img/t_logo.png", 
                              caption="Você escolheu nadica!")
    elif(query.data == '2'):
        context.bot.sendPhoto(chat_id=update.effective_chat.id,
                              photo=bot_functions.plot())
    else:
        query.edit_message_text(text="Você escolheu nada!")

def echo(update, context):
    vowels = ('a','e','i','o','u','A','E','I','O','U')
    x = update.message.text.upper()
    if x.startswith(vowels):
        x1 = x[:1]*10 + x[1:]
        x2 = x[:1]*5 + x[1:]
    else:
        x1 = x[:1] + x[1]*10 + x[2:]
        x2 = x[:1] + x[1]*5 + x[2:]
    context.bot.send_message(chat_id=update.effective_chat.id, text=x1)
    context.bot.send_message(chat_id=update.effective_chat.id, text=x2)
    context.bot.send_message(chat_id=update.effective_chat.id, text=x)

def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def inline_caps(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Desculpe, não entendo esse comando.")


# Add handlers to dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_command))
dispatcher.add_handler(CommandHandler('nada', nada))
dispatcher.add_handler(CommandHandler('caps', caps))

dispatcher.add_handler(CallbackQueryHandler(button))

dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

dispatcher.add_handler(InlineQueryHandler(inline_caps))