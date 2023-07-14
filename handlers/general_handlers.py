from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ChatActions, InputFile
from buttons.reply import reply_buttons_text
from buttons.reply.reply_buttons_text import ADD_OR_DELETE_USER_CATEGORIES_BUTTON_TEXT
from config.config import ADMINS
from create_bot import bot
from database.queries.get_queries import *
from database.queries.update_queries import update_user_last_post_id
from keyboards.reply.admin_keyboard import admin_panel_control_keyboard
from keyboards.reply.categories_keyboard import categories_admin_control_keyboard, categories_control_keyboard, \
    categories_keyboard
from keyboards.reply.personal_keyboard import personal_control_keyboard
from keyboards.reply.recommendations_keyboard import recommendations_control_keyboard, \
    recommendations_admin_control_keyboard
from store.states import UserStates
from utils.helpers import convert_categories_to_string


async def on_personal_feed_message(message: Message):
    await message.answer('Личная лента', reply_markup=personal_control_keyboard)


async def on_categories_feed_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    categories = await get_categories()
    user_categories = await get_user_categories(user_tg_id)
    await state.update_data(categories=categories)

    if user_categories:
        keyboard = categories_admin_control_keyboard if user_tg_id in ADMINS else categories_control_keyboard
        # Тут типо должна вызываться функция отправки постов, но пока стоит заглушка
        await message.answer('Лента категорий', reply_markup=keyboard)
    else:
        await on_add_or_delete_user_categories_message(message, state)


async def on_add_or_delete_user_categories_message(message: Message, state: FSMContext):
    context = await state.get_data()
    categories = context['categories'] or await get_categories()
    user_tg_id = message.from_user.id
    user_categories = await get_user_categories(user_tg_id)
    list_of_categories = '\n'.join(user_categories)
    keyboard = await categories_keyboard(categories)
    answer = '***Наш список категорий, но он обязательно будет обновляться:***\n\n'
    answer += await convert_categories_to_string(categories)
    answer += '\n‼***Чтобы удалить категорию нажмите на нее второй раз***‼'
    await message.answer(answer, reply_markup=keyboard, parse_mode='Markdown')
    await message.answer(f'Список выбранных категорий:\n{list_of_categories}')
    await state.set_state(UserStates.GET_USER_CATEGORIES)


async def on_start_message(message: Message, state: FSMContext):
    # Здесь запускаем функцию отправки постов. Пока стоит заглушка
    await state.reset_state()
    user_tg_id = message.from_user.id
    keyboard = categories_admin_control_keyboard if user_tg_id in ADMINS else categories_control_keyboard
    await message.answer('Посты из категорий', reply_markup=keyboard)


async def on_recommendations_feed_message(message: Message):
    user_tg_id = message.from_user.id
    user_is_admin = user_tg_id in ADMINS
    keyboard = recommendations_control_keyboard
    answer = 'Лента рекомендаций'

    if user_is_admin:
        keyboard = recommendations_admin_control_keyboard

    await message.answer(answer, reply_markup=keyboard)


async def on_admin_panel_message(message: Message):
    await message.answer('Админ панель', reply_markup=admin_panel_control_keyboard)


async def send_post_for_user_in_personal_lenta(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    personal_posts = await get_personal_posts(user_id)

    # try:
    if personal_posts:
        last_post_id = await get_user_last_post_id(user_id=message.from_user.id)

        next_post = None
        for post in personal_posts:
            if post.id > last_post_id:
                next_post = post
                break
            else:
                await message.answer("Посты закончились")
                break

        if next_post:
            text = next_post.text
            media_path = next_post.image_path
            channel_name = next_post.personal_channel_connection.username

            message_text = f"{text}\nChannel Name: @{channel_name}"

            if media_path is not None:
                if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_PHOTO)
                    await bot.send_photo(chat_id=chat_id, photo=InputFile(media_path), caption=message_text)
                elif media_path.lower().endswith(('.mp4', '.mov', '.avi')):
                    await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_VIDEO)
                    await bot.send_video(chat_id=chat_id, video=InputFile(media_path), caption=message_text)
            else:
                await bot.send_message(chat_id, text=message_text)

            await update_user_last_post_id(user_id, post.id)


async def send_post_for_user_in_recommendation(message: Message):
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

            if media_path is not None:
                if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_PHOTO)
                    await bot.send_photo(chat_id=chat_id, photo=InputFile(media_path), caption=message_text)
                elif media_path.lower().endswith(('.mp4', '.mov', '.avi')):
                    await bot.send_chat_action(chat_id, action=ChatActions.UPLOAD_VIDEO)
                    await bot.send_video(chat_id=chat_id, video=InputFile(media_path), caption=message_text)
            else:
                await bot.send_message(chat_id, text=message_text)

            await update_user_last_post_id(user_id, post.id)
        else:
            await message.answer("Посты закончились")
    else:
        await message.answer("Нет доступных постов")


def register_generals_handlers(dp):
    dp.register_message_handler(
        on_personal_feed_message,
        Text(equals=reply_buttons_text.TO_PERSONAL_BUTTON_TEXT),
    )

    dp.register_message_handler(
        on_categories_feed_message,
        Text(equals=reply_buttons_text.TO_CATEGORIES_BUTTON_TEXT)
    )

    dp.register_message_handler(
        on_recommendations_feed_message,
        Text(equals=reply_buttons_text.TO_RECOMMENDATIONS_BUTTON_TEXT)
    )

    dp.register_message_handler(
        on_admin_panel_message,
        Text(equals=reply_buttons_text.TO_ADMIN_PANEL_BUTTON_TEXT)
    )

    dp.register_message_handler(
        on_add_or_delete_user_categories_message,
        Text(equals=ADD_OR_DELETE_USER_CATEGORIES_BUTTON_TEXT)
    )
