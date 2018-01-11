import os
import qr_api
import telebot

bot = telebot.TeleBot(os.environ.get('token'))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(chat_id=message.chat.id, text='Send the text and I will make from it the QRCode, or send the QRCode and I will decrypt it.')

@bot.message_handler(content_types=['photo'])
def qr_handle(message):
    upload_msg = bot.reply_to(message, text='Uploading file...')
    try:
        file_info = bot.get_file(message.photo[1].file_id)
    except Exception as telebot_error:
        print(telebot_error)
        bot.edit_message_text(chat_id=message.chat.id, message_id=upload_msg.message_id, text='Maximum file size to upload is 20 MB.')
        return ''
    downloaded_file = bot.download_file(file_info.file_path)
    bot.edit_message_text(chat_id=message.chat.id, message_id=upload_msg.message_id, text='Scanning...')
    result = qr_api.read_qr(downloaded_file)
    if result['status']:
        bot.edit_message_text(chat_id=message.chat.id, message_id=upload_msg.message_id, text='*The data is decoded.\n\nResult:*\n{}'.format(result['result']), parse_mode='Markdown')
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=upload_msg.message_id, text='`{}`'.format(result['message']), parse_mode='Markdown')

@bot.message_handler()
def text_handle(message):
    markup = telebot.types.InlineKeyboardMarkup()
    create_button = telebot.types.InlineKeyboardButton(text='Create QRCode', callback_data='create')
    cancel_button = telebot.types.InlineKeyboardButton(text='Delete', callback_data='delete')
    markup.add(create_button)
    markup.add(cancel_button)
    bot.reply_to(message, text='Here\'s what I can do with this text.', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handle(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == 'delete':
        bot.answer_callback_query(callback_query_id=call.id, text='Okay :(')
    elif call.data == 'create':
        result = qr_api.create_qr(call.message.reply_to_message.text, call.message.from_user.id)
        if isinstance(result, dict):
            bot.reply_to(call.message.reply_to_message, text='`{}`'.format(result['message']), parse_mode='Markdown')
        else:
            bot.send_photo(chat_id=call.message.chat.id, photo=result, reply_to_message_id=call.message.reply_to_message.message_id)
            bot.answer_callback_query(callback_query_id=call.id, text='Hooray!')

if __name__ == '__main__':
    bot.polling(none_stop=True)
