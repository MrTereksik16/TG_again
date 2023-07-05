from aiogram import Bot, Dispatcher
from aiogram.types import Message
from telethon import TelegramClient
from telethon.tl.types import Channel

from config import config
from database.queries import create_user_channel, get_user, create_user, get_user_personal_channels
from logging_config import logger
from utils import strings

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
client = TelegramClient('session_name', config.API_ID, config.API_HASH)
client.start()


async def on_start_command(message: Message):
    user_tg_id = message.from_user.id
    user = await get_user(user_tg_id)
    if not user:
        await create_user(user_tg_id)
        await message.answer(strings.START_MESSAGE_FOR_NEW)
    else:
        await message.answer(strings.START_MESSAGE_FOR_OLD)


async def on_add_channels_command(message: Message):
    await message.answer(strings.ADD_CHANNELS_MESSAGE)


async def on_add_channels_message(message: Message):
    links = [link.strip() for link in message.text.split(',') if link.strip()]
    user_tg_id = message.from_user.id
    added = []
    not_added = []
    already_added = []
    for link in links:
        channel_tg_entity = Channel
        try:
            channel_tg_entity = await client.get_entity(link)
        except Exception as err:
            logger.error(f'Ошибка при получении сущности чата: {err}')

        result = await create_user_channel(user_tg_id, channel_tg_entity)
        if result == 'duplicate_entry':
            already_added.append(f'@{channel_tg_entity.username}')
        elif result:
            added.append(f'@{channel_tg_entity.username}')
        else:
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')

    message_text = ''
    if added:
        message_text += strings.CHANNELS_ADDED_MESSAGE.format(channels_added=", ".join(added))

    if not_added:
        message_text += strings.CHANNELS_NOT_ADDED_MESSAGE.format(channels_not_added=", ".join(not_added))
    if already_added:
        message_text += strings.CHANNELS_ALREADY_ADDED_MESSAGE.format(
            channels_already_added=", ".join(already_added))
    return await message.answer(message_text)


async def on_list_command(message: Message):
    user_tg_id = message.from_user.id
    channels = await get_user_personal_channels(user_tg_id)
    usernames = []
    if not channels:
        await message.answer('Список каналов пуст')
    else:
        for channel in channels:
            usernames.append(f'@{channel}')

        await message.answer(f'Добавленные каналы:\n{", ".join(usernames)}')









# async def on_start(message: Message):
# keyboard = ReplyKeyboardMarkup(keyboard=start_button, resize_keyboard=True)
# result = session.execute(select(User.user_tg_id)).all()
# user_tg_ids = [row[0] for row in result]
# if message.from_user.id not in user_tg_ids:
#     session.add(User(user_tg_id=message.from_user.id, last_post_id=123))
#     session.commit()
#     await message.reply("<b>Добро пожаловать дорогой, {message.from_user.first_name}!👨‍💻\n\nМы создали этого бота для твоего удобства, чтобы тебе было удобно пользоваться Телеграммом, источниками твоего вдохновения и отдыха 😇</b>",parse_mode="HTML",
#         reply_markup=keyboard)
# else:
#     await message.reply(f"<b>Рады вас снова видеть ,{message.from_user.first_name}😃</b>", reply_markup=keyboard, parse_mode="HTML")
