from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from config.config import ADMINS, SUPPORT_CHAT_ID
import callbacks
from create_bot import bot_client
from database.queries.get_queries import *
from database.queries.update_queries import *
from database.queries.delete_queries import delete_premium_channel_post, delete_category_channel_post, delete_personal_channel_post
from keyboards import admin_reply_keyboards
from keyboards import general_reply_buttons_texts
from keyboards.general.helpers import build_reactions_inline_keyboard
from store.states import *
from utils.custom_types import PostTypes, MarkTypes
from utils.helpers import send_post_to_support


async def on_admin_panel_message(message: Message, state: FSMContext):
    await state.set_state(AdminPanelStates.ADMIN_PANEL)
    user_tg_id = message.from_user.id
    if user_tg_id in ADMINS:
        await message.answer('<b>Админ панель</b>', reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)


async def on_like_button_click(callback: CallbackQuery):
    callback_pieces = callback.data.split(':')[1:]
    post_type = PostTypes(callback_pieces[0])
    post_id = int(callback_pieces[1])
    old_likes = int(callback_pieces[2])
    old_dislikes = int(callback_pieces[3])
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user_tg_id = callback.from_user.id
    message = callback.message

    mark_type = MarkTypes.LIKE
    post = None

    if post_type == PostTypes.PREMIUM:
        post = await get_premium_channel_post(post_id)
    elif post_type == PostTypes.CATEGORY:
        post = await get_category_channel_post(post_id)
    elif post_type == PostTypes.PERSONAL:
        post = await get_personal_channel_post(post_id)

    if not post:
        await callback.answer('Пост уже удалён')
        if hasattr(message.reply_to_message, 'message_id'):
            message_ids = list(range(message.reply_to_message.message_id, message.message_id + 1))
            return await bot_client.delete_messages(chat_id, message_ids)
        else:
            return await message.delete()

    new_likes = post.likes
    new_dislikes = post.dislikes

    if post_type == PostTypes.PREMIUM:
        premium_viewed_post = await get_viewed_premium_post(user_tg_id, post_id)
        mark_type = premium_viewed_post.mark_type_id

        if mark_type == MarkTypes.DISLIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_premium_post_mark_type(user_tg_id, post_id, MarkTypes.LIKE)
            await update_premium_post_likes(post_id)
            new_likes += 1
        if mark_type == MarkTypes.DISLIKE:
            await update_premium_post_dislikes(post_id, increment=False)
            new_dislikes -= 1

    elif post_type == PostTypes.CATEGORY:
        category_viewed_post = await get_viewed_category_post(user_tg_id, post_id)
        mark_type = category_viewed_post.mark_type_id

        if mark_type == MarkTypes.DISLIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_category_post_mark_type(user_tg_id, post_id, MarkTypes.LIKE)
            await update_category_post_likes(post_id)
            new_likes += 1
        if mark_type == MarkTypes.DISLIKE:
            await update_category_post_dislikes(post_id, increment=False)
            new_dislikes -= 1

    elif post_type == PostTypes.PERSONAL:
        personal_viewed_post = await get_viewed_personal_post(user_tg_id, post_id)
        mark_type = personal_viewed_post.mark_type_id

        if mark_type == MarkTypes.DISLIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_personal_post_mark_type(user_tg_id, post_id, MarkTypes.LIKE)
            await update_personal_post_likes(post_id)
            new_likes += 1
        if mark_type == MarkTypes.DISLIKE:
            await update_personal_post_dislikes(post_id, increment=False)
            new_dislikes -= 1

    keyboard = build_reactions_inline_keyboard(new_likes, new_dislikes, post_type, post_id)

    if mark_type == MarkTypes.LIKE:
        if new_likes != old_likes or new_dislikes != old_dislikes:
            await bot_client.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
            return await callback.answer('Обновлено')
        else:
            return await callback.answer('Вы можете лайкнуть пост единожды')

    await bot_client.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
    await callback.answer('Лайк')


async def on_dislike_button_click(callback: CallbackQuery):
    callback_pieces = callback.data.split(':')[1:]
    post_type = PostTypes(callback_pieces[0])
    post_id = int(callback_pieces[1])
    old_likes = int(callback_pieces[2])
    old_dislikes = int(callback_pieces[3])
    message = callback.message

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user_tg_id = callback.from_user.id

    mark_type = None
    post = None

    if post_type == PostTypes.PREMIUM:
        post = await get_premium_channel_post(post_id)
    elif post_type == PostTypes.CATEGORY:
        post = await get_category_channel_post(post_id)
    elif post_type == PostTypes.PERSONAL:
        post = await get_personal_channel_post(post_id)

    if not post:
        await callback.answer('Пост уже удалён')
        if hasattr(message.reply_to_message, 'message_id'):
            message_ids = list(range(message.reply_to_message.message_id, message.message_id + 1))
            return await bot_client.delete_messages(chat_id, message_ids)
        else:
            return await message.delete()

    new_likes = post.likes
    new_dislikes = post.dislikes

    if post_type == PostTypes.PREMIUM:
        mark_type = await get_viewed_premium_post(user_tg_id, post_id)

        if mark_type == MarkTypes.LIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_premium_post_mark_type(user_tg_id, post_id, MarkTypes.DISLIKE)
            await update_premium_post_dislikes(post_id)
            new_dislikes += 1
        if mark_type == MarkTypes.LIKE:
            await update_premium_post_likes(post_id, increment=False)
            new_likes -= 1

    elif post_type == PostTypes.CATEGORY:
        mark_type = await get_viewed_category_post(user_tg_id, post_id)

        if mark_type == MarkTypes.LIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_category_post_mark_type(user_tg_id, post_id, MarkTypes.DISLIKE)
            await update_category_post_dislikes(post_id)
            new_dislikes += 1

        if mark_type == MarkTypes.LIKE:
            await update_category_post_likes(post_id, increment=False)
            new_likes -= 1

    elif post_type == PostTypes.PERSONAL:
        mark_type = await get_viewed_personal_post(user_tg_id, post_id)

        if mark_type == MarkTypes.LIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_personal_post_mark_type(user_tg_id, post_id, MarkTypes.DISLIKE)
            await update_personal_post_dislikes(post_id)
            new_dislikes += 1

        if mark_type == MarkTypes.LIKE:
            await update_personal_post_likes(post_id, increment=False)
            new_likes -= 1

    keyboard = build_reactions_inline_keyboard(new_likes, new_dislikes, post_type, post_id)

    if mark_type == MarkTypes.DISLIKE:
        if new_likes != old_likes or new_dislikes != old_dislikes:
            await bot_client.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
            return await callback.answer('Обновлено')
        else:
            return await callback.answer('Вы можете дизлайкнуть пост единожды')

    await bot_client.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
    await callback.answer('Дизлайк')


async def on_report_button_click(callback: CallbackQuery):
    callback_pieces = callback.data.split(':')
    post_id = int(callback_pieces[2])
    post_type = callback_pieces[1]
    user_tg_id = callback.from_user.id
    chat_id = callback.message.chat.id
    message = callback.message

    viewed_post = None
    if post_type == PostTypes.PREMIUM:
        await update_premium_channel_post_reports(post_id)
        viewed_post = await get_viewed_premium_post(user_tg_id, post_id)
    elif post_type == PostTypes.CATEGORY:
        await update_category_channel_post_reports(post_id)
        viewed_post = await get_viewed_category_post(user_tg_id, post_id)
    elif post_type == PostTypes.PERSONAL:
        await update_personal_channel_post_reports(post_id)
        viewed_post = await get_viewed_personal_post(user_tg_id, post_id)

    if viewed_post:
        if viewed_post.mark_type_id == MarkTypes.REPORT:
            return await callback.answer('На пост можно пожаловаться единожды')

        if hasattr(viewed_post, 'personal_channel_id'):
            await update_viewed_personal_post_mark_type(user_tg_id, post_id, MarkTypes.REPORT)
        elif hasattr(viewed_post, 'premium_channel_id'):
            await update_viewed_premium_post_mark_type(user_tg_id, post_id, MarkTypes.REPORT)
        elif hasattr(viewed_post, 'category_channel_id'):
            await update_viewed_category_post_mark_type(user_tg_id, post_id, MarkTypes.REPORT)

        await callback.answer('Пост отправлен на рассмотрение')
    else:
        await callback.answer('Пост уже удалён')

    if hasattr(message.reply_to_message, 'message_id'):
        message_ids = list(range(message.reply_to_message.message_id, message.message_id + 1))
        await bot_client.delete_messages(chat_id, message_ids)
    else:
        await message.delete()

    await send_post_to_support(SUPPORT_CHAT_ID, viewed_post)


async def on_delete_post_button_click(callback: CallbackQuery):
    callback_pieces = callback.data.split(':')
    post_type = callback_pieces[1]
    post_id = int(callback_pieces[2])
    chat_id = callback.message.chat.id
    message = callback.message

    if post_type == PostTypes.PREMIUM:
        await delete_premium_channel_post(post_id)
    elif post_type == PostTypes.CATEGORY:
        await delete_category_channel_post(post_id)
    elif post_type == PostTypes.PERSONAL:
        await delete_personal_channel_post(post_id)

    await callback.answer('Пост удалён')
    if hasattr(message.reply_to_message, 'message_id'):
        message_ids = list(range(message.reply_to_message.message_id, message.message_id + 1))
        await bot_client.delete_messages(chat_id, message_ids)
    else:
        await message.delete()


def register_generals_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_admin_panel_message,
        Text(equals=general_reply_buttons_texts.TO_ADMIN_PANEL_BUTTON_TEXT),
        state='*'
    )
    dp.register_callback_query_handler(
        on_like_button_click,
        Text(startswith=callbacks.LIKE),
        state='*'
    )
    dp.register_callback_query_handler(
        on_dislike_button_click,
        Text(startswith=callbacks.DISLIKE),
        state='*'
    )

    dp.register_callback_query_handler(
        on_report_button_click,
        Text(startswith=callbacks.REPORT),
        state='*'
    )

    dp.register_callback_query_handler(
        on_delete_post_button_click,
        Text(startswith=callbacks.DELETE_POST),
        state='*'
    )
