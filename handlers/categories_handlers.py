from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ChatActions, InputFile, ContentType
from aiogram import Dispatcher

from config.config import ADMINS
from create_bot import bot

from buttons.reply.reply_buttons_text import *
from database.queries.create_queries import *
from database.queries.get_queries import *
from database.queries.update_queries import *
from database.queries.delete_queries import *
from handlers.general_handlers import on_start_message

from keyboards.reply.categories_keyboard import categories_control_keyboard, categories_admin_control_keyboard, \
    categories_keyboard
from store.states import UserStates
from utils.helpers import convert_categories_to_string



# Сомнительная конструкция. Потом обсудим
async def send_post_for_user(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    personal_posts = await get_personal_posts(user_id)

    try:
        if personal_posts:
            last_post_id = await get_user_last_post_id(user_id=message.from_user.id)

            next_post = None
            for post in personal_posts:
                if post.id > last_post_id:
                    next_post = post
                    break

            if next_post:
                text = next_post.text
                media_path = next_post.image_path
                channel_name = next_post.personal_channel_connection.username

                if media_path is not None:
                    if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        message_text = f"Text: {text}\nChannel Name: @{channel_name}"
                        await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_PHOTO)
                        await bot.send_photo(chat_id=chat_id, photo=InputFile(media_path), caption=message_text)

                    elif media_path.lower().endswith(('.mp4', '.mov', '.avi')):
                        message_text = f"Text: {text}\nChannel Name: @{channel_name}"
                        await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_VIDEO)
                        await bot.send_video(chat_id=chat_id, video=InputFile(media_path), caption=message_text)
                elif text is None or text == '':
                    if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        message_text = f"Channel Name: @{channel_name}"
                        await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_PHOTO)
                        await bot.send_photo(chat_id=chat_id, photo=InputFile(media_path), caption=message_text)

                    elif media_path.lower().endswith(('.mp4', '.mov', '.avi')):
                        message_text = f"Channel Name: @{channel_name}"
                        await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_VIDEO)
                        await bot.send_video(chat_id=chat_id, video=InputFile(media_path), caption=message_text)
                await update_user_last_post_id(user_id, post.id)
    except Exception as err:
        await message.answer('Посты закончились')
        logger.error(err)


async def on_categories_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    context = await state.get_data()
    categories = context['categories']

    if message.text == START_BUTTON_TEXT:
        return await on_start_message(message, state)

    elif message.text not in categories:
        return await message.answer('Такой категории у нас пока нет 😅')

    category_id = int(message.text[0])
    created = await create_user_category(user_tg_id, category_id)
    if created == errors.DUPLICATE_ENTRY_ERROR:
        deleted = await delete_user_category(user_tg_id, category_id)
        if deleted:
            await message.answer(f'Категория `{message.text.split(". ", 1)[1]}` удалена из списка ваших категорий',
                                 parse_mode='Markdown')
        else:
            await message.answer(f'Не удалось удалить категорию `{message.text[2:]}`', parse_mode='Markdown')

    elif created:
        await message.answer(f'Категория `{message.text.split(". ", 1)[1]}` добавлена в список ваших категорий',
                             parse_mode='Markdown')
    else:
        await message.answer('Упс. Что-то пошло не так')


def register_categories_handlers(dp: Dispatcher):
    dp.register_message_handler(
        send_post_for_user,
        Text(equals=SKIP_BUTTON_TEXT)
    )



    dp.register_message_handler(
        on_categories_message,
        content_types=ContentType.TEXT,
        state=UserStates.GET_USER_CATEGORIES
    )
