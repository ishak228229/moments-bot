import telebot
import datetime
from functions import typing, start_buttons, friends_menu, profile_menu, accept_friend
from conn import connection, cursor
from config import bot
import hashlib
from PIL import Image
from io import BytesIO
import time
from keep_alive import keep_alive

keep_alive()


@bot.message_handler(commands=['start'])
def start(message):
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS users (id int AUTO_INCREMENT, username varchar(32), password varchar(32), image longblob, description varchar(100), join_date varchar(32), friends longtext, _id varchar(32), PRIMARY KEY(id))"
  )
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS posts (id int AUTO_INCREMENT, username varchar(32), image longblob, description varchar(100), date varchar(32), PRIMARY KEY(id))"
  )
  connection.commit()

  cht = message.chat.id
  username = message.from_user.username

  if username == None:
    bot.send_message(
        cht,
        'Схоже, у тебе не встановлене <b>Ім\'я користувача</b>\nЙого необхідно встановити, щоб користуватись нашим сервісом'
    )
  else:
    cursor.execute("SELECT * FROM users WHERE username = %s", (username))
    data = cursor.fetchall()

    if len(data) == 0:
      time_now = datetime.datetime.now()
      date = time_now.strftime('%d.%m.%Y, %H:%M:%S')

      cursor.execute(
          "INSERT INTO users (username, join_date, _id) VALUES (%s, %s, %s)",
          (username, date, cht))
      connection.commit()

      bot.send_message(
          cht,
          'Привіт 👋\nГайда реєструватись та ділитсь найяскравішими мометами з друзями 📸'
      )
      msg = bot.send_message(
          cht, 'Давай заповнимо профіль!\nНадішли гарненьку аватарку ;)')
      bot.register_next_step_handler(msg, get_avatar)
    else:
      bot.send_message(cht,
                       'Привіт 👋\nПублікуємо нове фото?)',
                       reply_markup=start_buttons())


def get_avatar(message):
  cht = message.chat.id
  username = message.from_user.username

  try:
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path

    downloaded_file = bot.download_file(file_path)

    image = Image.open(BytesIO(downloaded_file))
    width, height = image.size

    aspect_ratio = width / height
    valid_aspect_ratios = [1 / 1]
    if aspect_ratio not in valid_aspect_ratios:
      raise ValueError(
          "Фото має мати співвідношення сторін 1:1\nОбріж його та спробуй ще раз 😉"
      )

    cursor.execute("UPDATE users SET image = %s WHERE username = %s",
                   (downloaded_file, username))
    connection.commit()

    bot.send_message(cht, 'Люкс 😻\nРухаємось далі!')
    msg = bot.send_message(cht,
                           'Придумай пароль 🔒\nНікому не повідомляй його 🤫')
    bot.register_next_step_handler(msg, get_password)
    # bot.send_message(cht, 'Тепер напиши який-небудь опис 💬\nРозкажи, наприклад, хто ти/що будеш публікувати...', get_description)
  except ValueError as ve:
    msg = bot.send_message(
        cht,
        'Фото має бути зі співвідношенням 1:1. Обріж його та спробуй ще раз 😉')
    bot.register_next_step_handler(msg, get_photo_post)
  except Exception as ex:
    msg = bot.send_message(cht,
                           'Халепа! Спробуй ще раз, або звернись у підтримку')
    bot.register_next_step_handler(msg, get_photo_post)


def get_password(message):
  cht = message.chat.id
  password = message.text
  hash = hashlib.md5()
  hash.update(password.encode())
  password_hash = hash.hexdigest()

  username = message.from_user.username

  try:
    cursor.execute("UPDATE users SET password = %s WHERE username = %s",
                   (password_hash, username))
    connection.commit()

    bot.send_message(cht, 'Люкс 😻\nРухаємось далі!')
    msg = bot.send_message(
        cht,
        'Тепер напиши який-небудь опис 💬\nРозкажи, наприклад, хто ти/що будеш публікувати...'
    )
    bot.register_next_step_handler(msg, get_description)
  except Exception as ex:
    msg = bot.send_message(
        cht, f'Халепа! Спробуй ще раз, або звернись у підтримку\n{ex}')
    bot.register_next_step_handler(msg, get_password)


def get_description(message):
  cht = message.chat.id
  username = message.from_user.username
  description = message.text

  try:
    cursor.execute("UPDATE users SET description = %s WHERE username = %s",
                   (description, username))
    connection.commit()

    bot.send_message(cht,
                     'Супер 👍\nУсе готово для першої публікації 😉',
                     reply_markup=start_buttons())
  except Exception as ex:
    msg = bot.send_message(cht,
                           'Халепа! Спробуй ще раз, або звернись у підтримку')
    bot.register_next_step_handler(msg, get_description)


def get_photo_post(message):
  cht = message.chat.id
  username = message.from_user.username

  try:
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path

    downloaded_file = bot.download_file(file_path)

    image = Image.open(BytesIO(downloaded_file))
    width, height = image.size

    aspect_ratio = width / height
    valid_aspect_ratios = [1 / 1, 3 / 4, 16 / 9, 4 / 3]
    if aspect_ratio not in valid_aspect_ratios:
      raise ValueError(
          "Фото має мати співвідношення сторін 1:1, 3:4, 16:9 або 4:3\nОбріж його та спробуй ще раз 😉"
      )

    time_now = datetime.datetime.now()
    date = time_now.strftime('%d.%m.%Y, %H:%M:%S')

    cursor.execute(
        "INSERT INTO posts (username, image, date) VALUES (%s, %s, %s)",
        (username, downloaded_file, date))
    connection.commit()

    bot.send_message(cht, 'Супер 😻')
    msg = bot.send_message(cht, 'Тепер напиши якийсь опис до фото 💬')
    bot.register_next_step_handler(msg, get_description_post, date)
  except ValueError as ve:
    msg = bot.send_message(
        cht,
        'Фото має бути зі співвідношенням 1:1, 3:4, 16:9 або 4:3. Спробуйте ще раз з іншим фото.'
    )
    bot.register_next_step_handler(msg, get_photo_post)
  except Exception as ex:
    msg = bot.send_message(cht,
                           'Халепа! Спробуй ще раз, або звернись у підтримку')
    bot.register_next_step_handler(msg, get_photo_post)


def get_description_post(message, date_):
  cht = message.chat.id
  description = message.text

  date = date_

  if description:
    try:
      cursor.execute("UPDATE posts SET description = %s WHERE date = %s",
                     (description, date))
      connection.commit()

      bot.send_message(cht,
                       'Супер 👍\nФото опубліковане, переглянь його у профілі',
                       reply_markup=start_buttons())
    except Exception as ex:
      msg = bot.send_message(
          cht, f'Халепа! Спробуй ще раз, або звернись у підтримку')
      bot.register_next_step_handler(msg, get_description_post, date)
  else:
    msg = bot.send_message(
        cht, f'Халепа! Спробуй ще раз, або звернись у підтримку')
    bot.register_next_step_handler(msg, get_description_post, date)


def get_friends(message):
  cht = message.chat.id
  username = message.from_user.username
  friend_name = message.text

  cursor.execute("SELECT * FROM users WHERE username = %s", (friend_name))
  data = cursor.fetchall()

  if len(data) > 0:
    id_ = data[0][7]

    cursor.execute("SELECT friends FROM users WHERE username = %s", (username))
    data2 = cursor.fetchone()

    data_list = data2[0].split(',')
    if friend_name not in data_list:
      added_friend = f'{data2[0]},{friend_name}'

      cursor.execute("UPDATE users SET friends = %s WHERE username = %s",
                     (added_friend, username))
      connection.commit()

      bot.send_message(cht,
                       f'Ти почав стежити за користувачем @{friend_name}',
                       reply_markup=friends_menu())
      msg = bot.send_message(id_,
                             f'Користувач {username} почав стежити за тобою',
                             reply_markup=accept_friend())
      bot.register_next_step_handler(msg, accept, username, friend_name, id_,
                                     cht)
    else:
      bot.send_message(cht,
                       f'Ти вже стежиш за користувачем @{friend_name}',
                       reply_markup=friends_menu())
  else:
    msg = bot.send_message(cht, 'Такого користувача не існує, спробуй ще раз')
    bot.register_next_step_handler(msg, get_friends)


def accept(message, username, friend_name, id_, cht):
  if message.text == 'Стежити ✅':
    cursor.execute("SELECT friends FROM users WHERE username = %s",
                   (friend_name))
    data2 = cursor.fetchone()
    added_friend = f'{data2[0]},{username}'

    cursor.execute("UPDATE users SET friends = %s WHERE username = %s",
                   (added_friend, friend_name))
    connection.commit()

    cursor.execute("SELECT friends FROM users WHERE username = %s",
                   (friend_name))
    f1 = cursor.fetchone()
    f1 = f1[0].split(',')
    cursor.execute("SELECT friends FROM users WHERE username = %s", (username))
    f2 = cursor.fetchone()
    f2 = f2[0].split(',')

    if friend_name in f2 and username in f1:
      bot.send_message(
          cht,
          f'Користувач @{friend_name} почав стежити за тобою\nТепер ви друзі 🤙',
          reply_markup=start_buttons())
      bot.send_message(
          id_,
          f'Ти почав стежити за користувачем @{username}\nТепер ви друзі 🤙',
          reply_markup=start_buttons())
  elif message.text == 'Не стежити ❌':
    ...


@bot.message_handler(content_types=['text'])
def text(message: telebot.types.Message) -> None:
  cht = message.chat.id
  username = message.from_user.username

  if message.text == '➕':
    msg = bot.send_message(
        cht,
        'Надішли фото, яке будемо публікувати 🚀\nВрахуй, що співвідношення сторін має бути 1:1, 3:4, 16:9 або 4:3',
        reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_photo_post)
  elif message.text == 'Профіль 👤':
    cursor.execute("SELECT * FROM users WHERE username = %s", (username))
    data = cursor.fetchone()
    cursor.execute("SELECT * FROM posts WHERE username = %s", (username))
    data2 = cursor.fetchall()
    bot.send_photo(cht,
                   photo=data[3],
                   caption=f'<b>@{data[1]}</b>\n' +
                   f'<blockquote><b>{data[4]}</b></blockquote>\n' +
                   f'<i>Опублковано:</i> <b>{len(data2)}</b> постів\n' +
                   f'<i>Приєднання:</i> <b>{data[5]}</b>',
                   parse_mode='HTML',
                   reply_markup=profile_menu())

  elif message.text == 'Друзі 🤝':
    bot.send_message(cht, 'Обери дію:', reply_markup=friends_menu())
  elif message.text == 'Додати друзів 🔍':
    msg = bot.send_message(cht,
                           'Введи ім\'я користувача',
                           reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_friends)
  elif message.text == 'Мої друзі 👥':
    cursor.execute("SELECT friends FROM users WHERE username = %s", (username))
    data = cursor.fetchone()

    if data[0] == None:
      bot.send_message(cht, 'У тебе поки немає друзів')
    else:
      friends_list = data[0].split(',')
      friends = ''
      k = 0

      for f in friends_list:
        if f != '':
          k = k + 1
          friends += f'<b>{k}</b>. <a href="http://192.168.1.249/user?username={f}">@{f}</a>\n'

      bot.send_message(cht, friends, parse_mode='HTML')

  if message.text == 'Головна 🏠':
    bot.send_message(cht,
                     'Привіт 👋\nПублікуємо нове фото?)',
                     reply_markup=start_buttons())

  if message.text == 'Мої публікації 🖼':
    cursor.execute("SELECT * FROM posts WHERE username = %s", (username))
    data = cursor.fetchall()


bot.polling()
