from aiogram.types import ChatActions, InputFile, KeyboardButton, Message
from config.config import ADMINS
from create_bot import client
from database.queries.create_queries import *
from database.queries.get_queries import *
from database.queries.update_queries import *
from keyboards.personal.inline.personal_inline_keyboards import add_user_channels_inline_keyboard
from parse import parse
from utils.consts import answers, errors
from keyboards import personal_reply_keyboards, recommendations_reply_keyboards, categories_reply_keyboards


async def convert_categories_to_string(categories) -> str:
    return ''.join([f'<code>{categories[i]}\n</code>' for i in range(0, len(categories))])


async def send_post_in_personal_feed(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id

    personal_posts = await get_personal_posts(user_tg_id)
    last_post_id = await get_user_last_personal_post_id(user_tg_id)
    user_channels = await get_user_channels(user_tg_id)
    keyboard = personal_reply_keyboards.personal_control_keyboard
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
            channel_username = next_post.username
            message_text = f"{text}\nChannel Name: @{channel_username}"
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

            await update_user_last_personal_post_id(user_tg_id, next_post.id)
    elif user_channels:
        for channel in user_channels:
            await parse(message, channel)
    else:
        await message.answer(answers.EMPTY_USER_LIST_CHANNELS_MESSAGE, reply_markup=add_user_channels_inline_keyboard)


async def send_post_in_recommendations_feed(message: Message):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    general_posts = await get_general_posts()
    keyboard = recommendations_reply_keyboards.recommendations_admin_control_keyboard if user_tg_id in ADMINS else recommendations_reply_keyboards.recommendations_control_keyboard

    if general_posts:
        last_post_id = await get_user_last_general_post_id(user_tg_id)
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

            await update_user_last_general_post_id(user_tg_id, next_post.id)
        else:
            await message.answer("Посты закончились")
    else:
        await message.answer("Нет доступных постов")


async def add_channels_from_message(message: Message,
                                    category='',
                                    ) -> dict[str | list[str]]:
    links = [link.strip() for link in message.text.split(',') if link.strip()]
    user_tg_id = message.from_user.id
    added = []
    not_added = []
    already_added = []
    admin_panel_mode = user_tg_id in ADMINS and category
    for link in links:
        try:
            channel_tg_entity = await client.get_entity(link)
        except Exception as err:
            logger.error(f'Ошибка при получении сущности чата: {err}')
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')
            continue

        channel_username = channel_tg_entity.username
        if admin_panel_mode:
            category_id = int(category[0])
            result = await create_general_channel(channel_username, category_id)
        else:
            result = await create_user_channel(user_tg_id, channel_username)

        if result == errors.DUPLICATE_ENTRY_ERROR:
            already_added.append(f'@{channel_username}')
        elif result:
            added.append(f'@{channel_username}')
        else:
            not_added.append(f'@{link.split("/")[-1].split("?")[0].replace("@", "")}')

    answer = ''
    if admin_panel_mode:
        if added:
            answer += answers.CHANNELS_ADDED_WITH_CATEGORY_MESSAGE.format(
                category=category.split(". ", 1)[1]) + ', '.join(added)
    else:
        if added:
            answer += answers.CHANNELS_ADDED_MESSAGE + ', '.join(added)

    if not_added:
        answer += answers.CHANNELS_NOT_ADDED_MESSAGE + ', '.join(not_added)
    if already_added:
        answer += answers.CHANNELS_ALREADY_ADDED_MESSAGE + ', '.join(already_added)

    return {'answer': answer, 'added': added, 'already_added': already_added, 'not_added': not_added}


async def create_categories_buttons(categories):
    categories_buttons = []
    for category in categories:
        categories_buttons.append(KeyboardButton(text=category))
    return categories_buttons
