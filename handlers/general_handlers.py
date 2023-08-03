from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from config.config import ADMINS
from callbacks import callbacks
from create_bot import bot_client
from database.queries.get_queries import get_viewed_category_post_mark_type, get_viewed_personal_post_mark_type, get_viewed_premium_post_mark_type
from database.queries.update_queries import *
from keyboards import admin_reply_keyboards
from keyboards import general_reply_buttons_texts
from store.states import *
from utils.helpers import create_reactions_keyboard
from utils.types import PostTypes, MarkTypes


async def on_admin_panel_message(message: Message, state: FSMContext):
    await state.set_state(AdminPanelStates.ADMIN_PANEL)
    user_tg_id = message.from_user.id
    if user_tg_id in ADMINS:
        await message.answer('<b>Админ панель</b>', reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)


async def on_like_button_click(callback: CallbackQuery):
    callback_pieces = callback.data.split(':')
    post_type = PostTypes(callback_pieces[1])
    post_id = int(callback_pieces[2])
    likes = int(callback_pieces[3])
    dislikes = int(callback_pieces[4])

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user_tg_id = callback.from_user.id

    mark_type = MarkTypes.LIKE
    print(post_type)
    if post_type == PostTypes.PREMIUM:
        mark_type = await get_viewed_premium_post_mark_type(post_id)

        if mark_type == MarkTypes.DISLIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_premium_post_mark_type(user_tg_id, post_id, MarkTypes.LIKE)
            await update_premium_post_likes(post_id)
            likes += 1
        if mark_type == MarkTypes.DISLIKE:
            await update_premium_post_dislikes(post_id, increment=False)
            dislikes -= 1

    elif post_type == PostTypes.CATEGORY:
        mark_type = await get_viewed_category_post_mark_type(post_id)

        if mark_type == MarkTypes.DISLIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_category_post_mark_type(user_tg_id, post_id, MarkTypes.LIKE)
            await update_category_post_likes(post_id)
            likes += 1
        if mark_type == MarkTypes.DISLIKE:
            await update_category_post_dislikes(post_id, increment=False)
            dislikes -= 1

    elif post_type == PostTypes.PERSONAL:
        mark_type = await get_viewed_personal_post_mark_type(post_id)
        print(mark_type)
        if mark_type == MarkTypes.DISLIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_personal_post_mark_type(user_tg_id, post_id, MarkTypes.LIKE)
            await update_personal_post_likes(post_id)
            likes += 1
        if mark_type == MarkTypes.DISLIKE:
            await update_personal_post_dislikes(post_id, increment=False)
            dislikes -= 1

    if mark_type == MarkTypes.LIKE:
        return await callback.answer('Вы можете лайкнуть пост единожды', show_alert=True)

    keyboard = create_reactions_keyboard(likes, dislikes, post_type, post_id)
    await callback.answer('Лайк')
    await bot_client.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)


async def on_dislike_button_click(callback: CallbackQuery):
    callback_pieces = callback.data.split(':')
    post_type = PostTypes(callback_pieces[1])
    post_id = int(callback_pieces[2])
    likes = int(callback_pieces[3])
    dislikes = int(callback_pieces[4])

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user_tg_id = callback.from_user.id

    mark_type = None

    if post_type == PostTypes.PREMIUM:
        mark_type = await get_viewed_premium_post_mark_type(post_id)

        if mark_type == MarkTypes.LIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_premium_post_mark_type(user_tg_id, post_id, MarkTypes.DISLIKE)
            await update_premium_post_dislikes(post_id)
            dislikes += 1
        if mark_type == MarkTypes.LIKE:
            await update_premium_post_likes(post_id, increment=False)
            likes -= 1

    elif post_type == PostTypes.CATEGORY:
        mark_type = await get_viewed_category_post_mark_type(post_id)

        if mark_type == MarkTypes.LIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_category_post_mark_type(user_tg_id, post_id, MarkTypes.DISLIKE)
            await update_category_post_dislikes(post_id)
            dislikes += 1

        if mark_type == MarkTypes.LIKE:
            await update_category_post_likes(post_id, increment=False)
            likes -= 1

    elif post_type == PostTypes.PERSONAL:
        mark_type = await get_viewed_personal_post_mark_type(post_id)

        if mark_type == MarkTypes.LIKE or mark_type == MarkTypes.NEUTRAL:
            await update_viewed_personal_post_mark_type(user_tg_id, post_id, MarkTypes.DISLIKE)
            await update_personal_post_dislikes(post_id)
            dislikes += 1

        if mark_type == MarkTypes.LIKE:
            await update_personal_post_likes(post_id, increment=False)
            likes -= 1

    if mark_type == MarkTypes.DISLIKE:
        return await callback.answer('Вы можете дизлайкнуть пост единожды', show_alert=True)

    keyboard = create_reactions_keyboard(likes, dislikes, post_type, post_id)
    await callback.answer('Дизлайк')
    await bot_client.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)


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
