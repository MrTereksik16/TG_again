from aiogram.types import Message, ChatActions, InputFile
from create_bot import bot
from database.queries.get_queries import *
from database.queries.update_queries import update_user_last_post_id
from keyboards.personal.inline.personal_inline_keyboards import add_user_channels_inline_keyboard
from parse import parse
from utils.consts import answers


async def convert_categories_to_string(categories) -> str:
    return ''.join([f'{categories[i]}\n' for i in range(0, len(categories))])


async def send_post_for_user_in_personal_feed(message: Message, keyboard):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id

    personal_posts = await get_personal_posts(user_tg_id)
    last_post_id = await get_user_last_post_id(user_tg_id)
    user_channels = await get_user_channels(user_tg_id)
    if personal_posts:
        next_post = None
        for post in personal_posts:
            if post.id > last_post_id:
                next_post = post
                break
        else:
            await message.answer(answers.POST_ARE_OVER, reply_markup=keyboard)

        if next_post:
            text = next_post.text
            media_path = next_post.image_path
            channel_name = next_post.username
            message_text = f"{text}\nChannel Name: @{channel_name}"
            try:
                if media_path is not None:
                    if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_PHOTO)
                        await bot.send_photo(chat_id=chat_id, photo=InputFile(media_path), caption=message_text,
                                             reply_markup=keyboard)
                    elif media_path.lower().endswith(('.mp4', '.mov', '.avi')):
                        await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_VIDEO)
                        await bot.send_video(chat_id=chat_id, video=InputFile(media_path), caption=message_text,
                                             reply_markup=keyboard)
                else:
                    await bot.send_message(chat_id, text=message_text, reply_markup=keyboard)
            except Exception as err:
                if 'Message caption is too long' in str(err):
                    await bot.answer('Упс. Пост слишком большой', reply_markup=keyboard)
                logger.error(f'Ошибка при отправлении поста пользователю: {err}')

            await update_user_last_post_id(user_tg_id, next_post.id)
    elif user_channels:
        for channel in user_channels:
            await parse(message, channel)
    else:
        await message.answer(answers.EMPTY_USER_LIST_CHANNELS_MESSAGE, reply_markup=add_user_channels_inline_keyboard)


async def send_post_for_user_in_recommendation(message: Message, keyboard):
    user_id = message.from_user.id
    chat_id = message.chat.id
    general_posts = await get_general_post()

    if general_posts:
        last_post_id = await get_user_last_post_id(user_id=message.from_user.id)

        next_post = None
        for post in general_posts:
            if post.id > last_post_id:
                next_post = post
                break
        if next_post:
            text = next_post.text
            media_path = next_post.image_path
            channel_name = next_post.general_channel_connection.username

            message_text = f"{text}\nChannel Name: @{channel_name}"
            try:
                if media_path is not None:
                    if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_PHOTO)
                        await bot.send_photo(chat_id=chat_id, photo=InputFile(media_path), caption=message_text,
                                             reply_markup=keyboard)
                    elif media_path.lower().endswith(('.mp4', '.mov', '.avi')):
                        await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_VIDEO)
                        await bot.send_video(chat_id=chat_id, video=InputFile(media_path), caption=message_text,
                                             reply_markup=keyboard)
                else:
                    await bot.send_message(chat_id, text=message_text)
            except Exception as err:
                if 'Message caption is too long' in str(err):
                    await bot.answer('Упс. Пост слишком большой', reply_markup=keyboard)
                logger.error(f'Ошибка при отправлении поста пользователю: {err}')
        else:
            await message.answer("Посты закончились")
    else:
        await message.answer("Нет доступных постов")
