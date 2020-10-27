from telegram.ext import CommandHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, Filters, MessageHandler

from bot_config import dispatcher
from utils import bot_messages
from utils import bot_utils
import bot_functions


# --- start, help and unknown comands ---

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=bot_messages.welcomeMessage)

def help_command(update, context):
    update.message.reply_text(bot_messages.helpMessage)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=bot_messages.unknown)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_command))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))


# --- plots ---

plot_argws = {'type': "", 'param': "", 'line': "", 'element': ""}
TYPE, PARAM, LINE, ELEMENT = range(4)
to_delete = None

def plot(update, context):
    global plot_argws
    plot_argws = {'type': "", 'param': "", 'line': "", 'element': ""}

    update.message.reply_text("📈 Visualização gráfica de medições")
    kb = [[KeyboardButton(bot_messages.sensors)],
          [KeyboardButton(bot_messages.contingency)]]
    kb_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Selecione o tipo:", 
                              reply_markup=kb_markup)
    return TYPE


def get_type(update, context):
    plot_argws['type'] = update.message.text

    if update.message.text == bot_messages.sensors:
        kb = [[KeyboardButton('3 segundos')],
             [KeyboardButton('20 segundos')]]
        kb_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('Selecione parâmetros adicionais', 
                                  reply_markup=kb_markup)
    elif update.message.text == bot_messages.contingency:
        kb = [[KeyboardButton(bot_messages.severity)],
             [KeyboardButton(bot_messages.abcd_classification)]]
        kb_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('Selecione parâmetros adicionais', 
                                  reply_markup=kb_markup)
    else:
        update.message.reply_text(bot_messages.unknown)
        return TYPE

    return PARAM


def get_param(update, context):
    plot_argws['param'] = update.message.text

    update.message.reply_text(f"Indique uma linha:",
                              reply_markup=ReplyKeyboardRemove())

    return LINE


def get_line(update, context):
    lines = bot_functions.list_lines(plot_argws)
    lines = [l.casefold() for l in lines]
    if not update.message.text.casefold() in lines:
        update.message.reply_text(f"""❌ Não foi possível identificar a linha: {update.message.text}\n\n
Selecione /lines para listar todas as linhas disponíveis""")
        return LINE

    plot_argws['line'] = update.message.text.upper()

    global to_delete
    if not to_delete is None:
        to_delete.delete()
        to_delete = None
    update.message.reply_text(f"Indique um elemento:")

    return ELEMENT


def get_element(update, context):
    elements = bot_functions.list_elements(plot_argws)
    elements = [l.casefold() for l in elements]
    if not update.message.text.casefold() in elements:
        update.message.reply_text(f"""❌ Não foi possível identificar o elemento: {update.message.text}\n\n
Selecione /elements para listar todas os elementos disponíveis""")
        return ELEMENT
    
    plot_argws['element'] = update.message.text.upper()

    global to_delete
    if not to_delete is None:
        to_delete.delete()
        to_delete = None
    msg = '''Tipo: {}
{}
Local: {}
Elemento: {}'''.format(plot_argws['type'], plot_argws['param'], plot_argws['line'], plot_argws['element'])
    update.message.reply_text(msg)
    to_delete = update.message.reply_text(bot_messages.searching)
    
    if plot_argws['type'] == bot_messages.sensors:
        media = bot_functions.sensors_plot(plot_argws)

    elif plot_argws['type'] == bot_messages.contingency:
        table = bot_functions.contingency_table(plot_argws)
        media = bot_functions.contingency_plot(plot_argws)
        
        if table is None:
            update.message.reply_text(bot_messages.unknown,
                                    reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        
        if not to_delete is None:
            to_delete.delete()
            to_delete = None
        
        context.bot.send_photo(chat_id=update.effective_chat.id, 
                           photo=table, 
                           reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(bot_messages.understand)
        update.message.reply_text(bot_messages.instructions)
        return ConversationHandler.END

    if media is None:
        update.message.reply_text(bot_messages.unknown,
                                  reply_markup=ReplyKeyboardRemove())
    elif isinstance(media, list):
        context.bot.send_media_group(chat_id=update.effective_chat.id, 
                                     media=media, 
                                     reply_markup=ReplyKeyboardRemove())
    else:
        context.bot.send_photo(chat_id=update.effective_chat.id, 
                               photo=media, 
                               reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def list_lines(update, context):
    global to_delete

    lines = bot_functions.list_lines(plot_argws)
    lines.sort()
    lines = '\n'.join(lines)
    to_delete = update.message.reply_text(f"Linhas disponíveis\n\n{lines}")
    update.message.reply_text(f"Indique uma linha:")
    
    return LINE


def list_elements(update, context):
    global to_delete
    
    elements = bot_functions.list_elements(plot_argws)
    elements.sort()
    elements = '\n'.join(elements)
    to_delete = update.message.reply_text(f"Elementos disponíveis\n\n{elements}")
    update.message.reply_text(f"Indique um elemento:")
    
    return ELEMENT


def cancel(update, context):
    update.message.reply_text(bot_messages.cancel,
			                  reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


plot_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('plot', plot)],
    states={
        TYPE: [
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.text, get_type)
        ],
        PARAM: [
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.text, get_param)
        ],
        LINE: [
            CommandHandler('cancel', cancel),
            CommandHandler('lines', list_lines),
            MessageHandler(Filters.text, get_line)
        ],
        ELEMENT: [
            CommandHandler('cancel', cancel),
            CommandHandler('elements', list_elements),
            MessageHandler(Filters.text, get_element)
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)                

dispatcher.add_handler(plot_conversation_handler)
