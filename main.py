import requests
from PIL import Image
import telebot
import threading
import io


URL = 'https://pixel.vkforms.ru/data/1.bmp'
SAFE_COORD = (0, 0, 1590, 400)  # (left, top, right, bottom)
TOKEN = '12345:AAAAAAAAAAAAAA'  # Telegram bot api token
FILENAME = '1.bmp'

main_image = None
bot = telebot.TeleBot(TOKEN)


def get_image(filename):
    return Image.open(filename)


def download_image(url, filename):
    threading.Timer(60.0, download_image).start()
    global main_image
    with open(filename, 'wb') as file:
        file.write(requests.get(url).content)
    main_image = get_image(filename)


def crop_image(image, coord):
    return image.crop(coord)


# TODO: make this shit more readable
def get_coord(coord):
    return tuple(
            max(SAFE_COORD[i], coord[i]) for i in range(2)) +\
           tuple(
            min(SAFE_COORD[i], coord[i]) for i in range(2, 4))


@bot.message_handler(commands=['get'])
def send_crop_image(message):
    coord = tuple((int(el) for el in message.text.split()[1:]))
    if len(coord) < 4:
        return

    bot.send_chat_action(message.chat.id, 'upload_photo')

    with crop_image(main_image, get_coord(coord)) as img:
        imgbytes = io.BytesIO()
        img.save(imgbytes, format='PNG')
        bot.send_photo(message.chat.id,
                       imgbytes.getvalue(),
                       reply_to_message_id=message.message_id)


def main():
    download_image(URL, FILENAME)
    bot.polling()


if __name__ == '__main__':
    main()
