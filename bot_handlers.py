from telegram.ext import CommandHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, Filters, MessageHandler

from bot_config import dispatcher
from utils import bot_messages, bot_utils
import bot_functions
import locale
from locale import atof
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


# --- start and help comands ---

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=bot_messages.welcomeMessage)

def help_command(update, context):
    update.message.reply_text(bot_messages.helpMessage)

 
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_command))


to_delete = None

# --- plots ---

KM, ELEMENT, LINE, TYPE, PARAM = range(5)
plot_argws = {'by': "", # E: element/line, K: km
              'km': "", 
              'element': "", 'line': "", 
              'type': "", 'param': ""}

def blanc_plot_argws():
    global plot_argws
    plot_argws = {'by': "",'km': "",'element': "",'line': "",'type': "",'param': ""}
    return plot_argws


# --- plots by line/element ---

def plot_elements(update, context):
    plot_argws = blanc_plot_argws()
    plot_argws['by'] = 'E'

    update.message.reply_text(bot_messages.plot,
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(f"Indique um elemento:")
    
    return ELEMENT


def get_element(update, context):
    elements = bot_functions.list_elements()
    elements = [l.casefold() for l in elements]
    if not update.message.text.casefold() in elements:
        update.message.reply_text(f"""❌ Não foi possível identificar o elemento: {update.message.text}\n\n
Selecione /elementos para listar todas os elementos disponíveis""")
        return ELEMENT

    plot_argws['element'] = update.message.text.upper()
    global to_delete
    if not to_delete is None:
        to_delete.delete()
        to_delete = None
    update.message.reply_text(f"Indique uma linha:",
                              reply_markup=ReplyKeyboardRemove())

    return LINE


def get_line(update, context):
    lines = bot_functions.list_lines(plot_argws['element'])
    lines = [l.casefold() for l in lines]
    if not update.message.text.casefold() in lines:
        update.message.reply_text(f"""❌ Não foi possível identificar a linha: {update.message.text}\n\n
Selecione /linhas para listar todas as linhas disponíveis""")
        return LINE

    plot_argws['line'] = update.message.text.upper()
    global to_delete
    if not to_delete is None:
        to_delete.delete()
        to_delete = None

    kb = [[KeyboardButton(bot_messages.sensors)],
          [KeyboardButton(bot_messages.contingency)],
          [KeyboardButton(bot_messages.speed_restriction)]]
    kb_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Selecione o tipo:", 
                              reply_markup=kb_markup)

    return TYPE


def get_type(update, context):
    plot_argws['type'] = update.message.text

    if update.message.text == bot_messages.sensors:
        kb = [[KeyboardButton(bot_messages.three_seconds)],
             [KeyboardButton(bot_messages.twenty_seconds)]]
        msg = "Selecione o período:"
    elif update.message.text == bot_messages.contingency:
        kb = [[KeyboardButton(bot_messages.severity)],
             [KeyboardButton(bot_messages.abcd_classification)]]
        msg = "Selecione o tipo de contingência:"
    elif update.message.text == bot_messages.speed_restriction:
        kb = [[KeyboardButton(bot_messages.acceleration), KeyboardButton(bot_messages.bodyrock)],
              [KeyboardButton(bot_messages.suspentiontravel), KeyboardButton(bot_messages.bounce)]]
        msg = "Selecione a variável dinâmica:"
    else:
        update.message.reply_text(bot_messages.unknown)
        return TYPE

    kb_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(msg, 
                              reply_markup=kb_markup)

    return PARAM


def get_param(update, context):
    plot_argws['param'] = update.message.text

    if plot_argws['by'] == 'E':
        msg = '{}\n{}\nLinha: {}\nElemento: {}'.format(plot_argws['type'], 
                                                       plot_argws['param'], 
                                                       plot_argws['line'], 
                                                       plot_argws['element'])
    elif plot_argws['by'] == 'K':
        msg = '{}\n{}\nKm {}'.format(plot_argws['type'], 
                                     plot_argws['param'], 
                                     ','.join(map(str, plot_argws['km'])))
    else:
        wrong_plot(update, context)

    update.message.reply_text(msg,
                              reply_markup=ReplyKeyboardRemove())
    to_delete = update.message.reply_text(bot_messages.searching)
    table = media = None
    
    if plot_argws['type'] == bot_messages.sensors:
        media = bot_functions.sensors_plot(plot_argws)

    elif plot_argws['type'] == bot_messages.contingency:
        table = bot_functions.contingency_table(plot_argws)
        media = bot_functions.contingency_plot(plot_argws)

    elif plot_argws['type'] == bot_messages.speed_restriction:
        media = bot_functions.rest_velocidade_plot(plot_argws)

    else:
        wrong_plot(update, context)

    if not to_delete is None:
        to_delete.delete()
        to_delete = None

    if not table is None:
        context.bot.send_photo(chat_id=update.effective_chat.id, 
                               photo=table)
    if media is None:
        update.message.reply_text(bot_messages.understand)
    elif isinstance(media, list):
        context.bot.send_media_group(chat_id=update.effective_chat.id, 
                                     media=media)
    else:
        context.bot.send_photo(chat_id=update.effective_chat.id, 
                               photo=media)

    return ConversationHandler.END


def list_elements(update, context):
    global to_delete

    elements = bot_functions.list_elements()
    elements = '\n'.join(elements)
    to_delete = update.message.reply_text(f"Elementos disponíveis\n\n{elements}")
    update.message.reply_text(f"Indique um elemento:")

    return ELEMENT


def list_lines(update, context):
    global to_delete

    lines = bot_functions.list_lines(plot_argws['element'])
    lines = '\n'.join(lines)
    to_delete = update.message.reply_text(f"Linhas disponíveis\n\n{lines}")
    update.message.reply_text(f"Indique uma linha:")
    
    return LINE


# --- plots by km ---

def plot_km(update, context):
    plot_argws = blanc_plot_argws()
    plot_argws['by'] = 'K'
    
    lo, hi = bot_functions.range_km()
    update.message.reply_text(bot_messages.plot,
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_text("Indique uma ou mais posições entre %.2f e %.2f separadas por vírgula:" % (lo, hi))

    return KM


def get_km(update, context):
    lo, hi = bot_functions.range_km()
    try:
        km = update.message.text
        km = [atof(k.strip().replace('.',',')) for k in km.split(',')]
    except ValueError:
        km = [None]
    for k in km:
        if k is None or k < lo or k > hi:
            update.message.reply_text(f"""❌ Posição {k} incorreta!\n\n
Indique uma ou mais posições entre %.2f e %.2f separadas por vírgula:""" % (lo, hi))
            return KM

    plot_argws['km'] = km

    if len(km) > 1:
        kb = [[KeyboardButton(bot_messages.speed_restriction)]]
    else:
        kb = [[KeyboardButton(bot_messages.sensors)],
              [KeyboardButton(bot_messages.contingency)],
              [KeyboardButton(bot_messages.speed_restriction)]]
    kb_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Selecione o tipo:", 
                              reply_markup=kb_markup)

    return TYPE


def wrong_plot(update, context):
    update.message.reply_text(bot_messages.understand, 
                              reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(bot_messages.instructions)
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text(bot_messages.cancel,
			                  reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


plot_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('elemento', plot_elements), 
                  CommandHandler('km', plot_km)],
    states={
        KM: [
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.text, get_km)
        ],
        ELEMENT: [
            CommandHandler('cancel', cancel),
            CommandHandler('elementos', list_elements),
            MessageHandler(Filters.text, get_element)
        ],
        LINE: [
            CommandHandler('cancel', cancel),
            CommandHandler('linhas', list_lines),
            MessageHandler(Filters.text, get_line)
        ],
        TYPE: [
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.text, get_type)
        ],
        PARAM: [
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.text, get_param)
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(plot_conversation_handler)


# --- unknown comands ---

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=bot_messages.unknown, 
                             reply_markup=ReplyKeyboardRemove())

dispatcher.add_handler(MessageHandler(Filters.command, unknown))
