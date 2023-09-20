from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from config.config import ADMINS
from create_bot import bot_client
from database.queries.get_queries import *
from database.queries.update_queries import *
from database.queries.delete_queries import delete_premium_channel_post, delete_category_channel_post, delete_user_channel_post
from keyboards import admin_reply_keyboards
from keyboards import general_reply_buttons_texts
from keyboards.categories.reply import categories_reply_keyboards
from keyboards.general.helpers import build_reactions_inline_keyboard, build_reply_buttons, build_reply_keyboard
from keyboards.personal.reply import personal_reply_keyboards
from keyboards.recommendations.reply import recommendations_reply_keyboards
from store.states import *
from utils.consts import answers, callbacks, commands
from utils.custom_types import ChannelPostTypes, MarkTypes, Modes
from utils.helpers import send_post_to_support, get_next_post, send_next_post, send_end_message, reset_and_switch_state


async def on_guide_command(message: Message):
    return await message.answer(answers.GUIDE_MESSAGE_TEXT)


async def on_start_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_is_admin = user_tg_id in ADMINS
    chat_id = message.chat.id
    current_state = await state.get_state()
    await update_last_visit_time(user_tg_id)

    if current_state == RecommendationsStates.RECOMMENDATIONS_FEED.state:
        mode = Modes.RECOMMENDATIONS
        next_post = await get_next_post(user_tg_id, mode)
        keyboard = recommendations_reply_keyboards.recommendations_control_keyboard

    elif current_state == CategoriesStates.CATEGORIES_FEED.state:
        mode = Modes.CATEGORIES
        user_categories = await get_user_categories(user_tg_id)
        keyboard = categories_reply_keyboards.categories_control_keyboard

        if not user_categories:
            await reset_and_switch_state(state, CategoriesStates.GET_USER_CATEGORIES)
            return await message.answer('Сперва нужно добавить хотя бы одну категорию')

        await reset_and_switch_state(state, CategoriesStates.CATEGORIES_FEED)
        next_post = await get_next_post(user_tg_id, mode)

    elif current_state == PersonalStates.PERSONAL_FEED.state:
        user_channels = await get_user_channels_usernames(user_tg_id)
        if not user_channels:
            return await message.answer('Сперва нужно добавить хотя бы один канал')
        keyboard = personal_reply_keyboards.personal_control_keyboard
        mode = Modes.PERSONAL
        next_post = await get_next_post(user_tg_id, mode)
    else:
        return None

    if user_is_admin and current_state != PersonalStates.PERSONAL_FEED.state:
        keyboard = recommendations_reply_keyboards.recommendations_admin_control_keyboard
        if current_state == CategoriesStates.CATEGORIES_FEED.state:
            keyboard = categories_reply_keyboards.categories_admin_control_keyboard

    if next_post:
        await message.answer(answers.PRE_SCROLL_MESSAGE_TEXT, reply_markup=keyboard)
        await send_next_post(user_tg_id, chat_id, mode, next_post)
    else:
        await send_end_message(user_tg_id, chat_id, mode)


async def on_skip_message(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    chat_id = message.chat.id
    current_state = await state.get_state()
    await update_last_visit_time(user_tg_id)

    if current_state == RecommendationsStates.RECOMMENDATIONS_FEED.state:
        mode = Modes.RECOMMENDATIONS
        await send_next_post(user_tg_id, chat_id, mode)
    elif current_state == CategoriesStates.CATEGORIES_FEED.state:
        mode = Modes.CATEGORIES
        await send_next_post(user_tg_id, chat_id, mode)
    elif current_state == PersonalStates.PERSONAL_FEED.state:
        mode = Modes.PERSONAL
        await send_next_post(user_tg_id, chat_id, mode)
    else:
        return None


async def on_admin_panel_message(message: Message, state: FSMContext):
    await state.set_state(AdminPanelStates.ADMIN_PANEL)
    user_tg_id = message.from_user.id
    if user_tg_id in ADMINS:
        await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)


async def on_like_button_click(callback: CallbackQuery):
    callback_pieces = callback.data.split(':')[1:]
    post_type = ChannelPostTypes(callback_pieces[0])
    post_id = int(callback_pieces[1])
    old_likes = int(callback_pieces[2])
    old_dislikes = int(callback_pieces[3])
    mode = Modes(callback_pieces[4])

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user_tg_id = callback.from_user.id
    message = callback.message

    mark_type_id = MarkTypes.LIKE
    post = None
    if post_type == ChannelPostTypes.PREMIUM:
        post = await get_premium_channel_post(post_id)
    elif post_type == ChannelPostTypes.CATEGORY:
        post = await get_category_channel_post(post_id)
    elif post_type == ChannelPostTypes.PERSONAL:
        post = await get_personal_channel_post(post_id)

    if not post:
        await callback.answer('Пост уже удалён')
        if hasattr(message.reply_to_message, 'message_id'):
            message_ids = list(range(message.reply_to_message.message_id, message.message_id + 1))
            return await bot_client.delete_messages(chat_id, message_ids)
        else:
            message_ids = message.message_id
            return await bot_client.delete_messages(chat_id, message_ids)

    new_likes = post.likes
    new_dislikes = post.dislikes

    if post_type == ChannelPostTypes.PREMIUM:
        premium_viewed_post = await get_viewed_premium_post(user_tg_id, post_id)
        mark_type_id = premium_viewed_post.mark_type_id

        if mark_type_id == MarkTypes.DISLIKE or mark_type_id == MarkTypes.NEUTRAL:
            await update_viewed_premium_post_mark_type(user_tg_id, post_id, MarkTypes.LIKE)
            new_likes = await update_premium_post_likes(post_id)
        if mark_type_id == MarkTypes.DISLIKE:
            new_dislikes = await update_premium_post_dislikes(post_id, increment=False)

    elif post_type == ChannelPostTypes.CATEGORY:
        category_viewed_post = await get_viewed_category_post(user_tg_id, post_id)
        mark_type_id = category_viewed_post.mark_type_id

        if mark_type_id == MarkTypes.DISLIKE or mark_type_id == MarkTypes.NEUTRAL:
            await update_viewed_category_post_mark_type(user_tg_id, post_id, MarkTypes.LIKE)
            new_likes = await update_category_post_likes(post_id)
        if mark_type_id == MarkTypes.DISLIKE:
            new_dislikes = await update_category_post_dislikes(post_id, increment=False)

    elif post_type == ChannelPostTypes.PERSONAL:
        personal_viewed_post = await get_viewed_personal_post(user_tg_id, post_id)
        mark_type_id = personal_viewed_post.mark_type_id

        if mark_type_id == MarkTypes.DISLIKE or mark_type_id == MarkTypes.NEUTRAL:
            await update_viewed_personal_post_mark_type(user_tg_id, post_id, MarkTypes.LIKE)
            new_likes = await update_personal_post_likes(post_id)
        if mark_type_id == MarkTypes.DISLIKE:
            new_dislikes = await update_personal_post_dislikes(post_id, increment=False)

    keyboard = build_reactions_inline_keyboard(new_likes, new_dislikes, post_type, post_id, mode)

    if mark_type_id == MarkTypes.LIKE:
        if new_likes != old_likes or new_dislikes != old_dislikes:
            await bot_client.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
            await callback.answer('Обновлено')
        else:
            await callback.answer('Вы можете лайкнуть пост единожды')
        return await send_next_post(user_tg_id, chat_id, mode)
    elif mark_type_id == MarkTypes.DISLIKE or mark_type_id == MarkTypes.NEUTRAL:
        await update_daily_likes()
        if mark_type_id == MarkTypes.DISLIKE:
            await update_daily_dislikes(increment=False)

    await bot_client.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
    await callback.answer('Лайк')
    await send_next_post(user_tg_id, chat_id, mode)


async def on_dislike_button_click(callback: CallbackQuery):
    callback_pieces = callback.data.split(':')[1:]
    post_type = ChannelPostTypes(callback_pieces[0])
    post_id = int(callback_pieces[1])
    old_likes = callback_pieces[2]
    old_dislikes = callback_pieces[3]
    mode = Modes(callback_pieces[4])

    message = callback.message
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user_tg_id = callback.from_user.id

    mark_type_id = None
    post = None
    if post_type == ChannelPostTypes.PREMIUM:
        post = await get_premium_channel_post(post_id)
    elif post_type == ChannelPostTypes.CATEGORY:
        post = await get_category_channel_post(post_id)
    elif post_type == ChannelPostTypes.PERSONAL:
        post = await get_personal_channel_post(post_id)

    if not post:
        await callback.answer('Пост уже удалён')
        if hasattr(message.reply_to_message, 'message_id'):
            message_ids = list(range(message.reply_to_message.message_id, message.message_id + 1))
            return await bot_client.delete_messages(chat_id, message_ids)
        else:
            message_ids = message.message_id
            return await bot_client.delete_messages(chat_id, message_ids)

    new_likes = post.likes
    new_dislikes = post.dislikes

    if post_type == ChannelPostTypes.PREMIUM:
        category_viewed_post = await get_viewed_premium_post(user_tg_id, post_id)
        mark_type_id = category_viewed_post.mark_type_id

        if mark_type_id == MarkTypes.LIKE or mark_type_id == MarkTypes.NEUTRAL:
            await update_viewed_premium_post_mark_type(user_tg_id, post_id, MarkTypes.DISLIKE)
            new_dislikes = await update_premium_post_dislikes(post_id)
        if mark_type_id == MarkTypes.LIKE:
            new_likes = await update_premium_post_likes(post_id, increment=False)

    elif post_type == ChannelPostTypes.CATEGORY:
        category_viewed_post = await get_viewed_category_post(user_tg_id, post_id)
        mark_type_id = category_viewed_post.mark_type_id

        if mark_type_id == MarkTypes.LIKE or mark_type_id == MarkTypes.NEUTRAL:
            await update_viewed_category_post_mark_type(user_tg_id, post_id, MarkTypes.DISLIKE)
            new_dislikes = await update_category_post_dislikes(post_id)

        if mark_type_id == MarkTypes.LIKE:
            new_likes = await update_category_post_likes(post_id, increment=False)

    elif post_type == ChannelPostTypes.PERSONAL:
        category_viewed_post = await get_viewed_personal_post(user_tg_id, post_id)
        mark_type_id = category_viewed_post.mark_type_id

        if mark_type_id == MarkTypes.LIKE or mark_type_id == MarkTypes.NEUTRAL:
            await update_viewed_personal_post_mark_type(user_tg_id, post_id, MarkTypes.DISLIKE)
            new_dislikes = await update_personal_post_dislikes(post_id)

        if mark_type_id == MarkTypes.LIKE:
            new_likes = await update_personal_post_likes(post_id, increment=False)

    keyboard = build_reactions_inline_keyboard(new_likes, new_dislikes, post_type, post_id, mode)

    if mark_type_id == MarkTypes.DISLIKE:
        if new_likes != old_likes or new_dislikes != old_dislikes:
            await bot_client.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
            await callback.answer('Обновлено')
        else:
            await callback.answer('Вы можете дизлайкнуть пост единожды')
        return await send_next_post(user_tg_id, chat_id, mode)
    elif mark_type_id == MarkTypes.LIKE or mark_type_id == MarkTypes.NEUTRAL:
        await update_daily_dislikes()
        if mark_type_id == MarkTypes.LIKE:
            await update_daily_likes(increment=False)

    await bot_client.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
    await callback.answer('Дизлайк')

    await send_next_post(user_tg_id, chat_id, mode)


async def on_report_button_click(callback: CallbackQuery):
    callback_pieces = callback.data.split(':')[1:]
    post_type = callback_pieces[0]
    post_id = int(callback_pieces[1])
    mode = Modes(callback_pieces[2])

    user_tg_id = callback.from_user.id
    chat_id = callback.message.chat.id
    message = callback.message

    viewed_post = None
    if post_type == ChannelPostTypes.PREMIUM:
        await update_premium_channel_post_reports(post_id)
        viewed_post = await get_viewed_premium_post(user_tg_id, post_id)
    elif post_type == ChannelPostTypes.CATEGORY:
        await update_category_channel_post_reports(post_id)
        viewed_post = await get_viewed_category_post(user_tg_id, post_id)
    elif post_type == ChannelPostTypes.PERSONAL:
        await update_personal_channel_post_reports(post_id)
        viewed_post = await get_viewed_personal_post(user_tg_id, post_id)

    if viewed_post:
        mark_type_id = MarkTypes.REPORT
        if viewed_post.mark_type_id == mark_type_id:
            return await callback.answer('На пост можно пожаловаться единожды')

        if hasattr(viewed_post, 'personal_channel_id'):
            await update_viewed_personal_post_mark_type(user_tg_id, post_id, mark_type_id)
        elif hasattr(viewed_post, 'premium_channel_id'):
            await update_viewed_premium_post_mark_type(user_tg_id, post_id, mark_type_id)
        elif hasattr(viewed_post, 'category_channel_id'):
            await update_viewed_category_post_mark_type(user_tg_id, post_id, mark_type_id)

        await callback.answer('Пост отправлен на рассмотрение')
    else:
        await callback.answer('Пост уже удалён')

    await send_next_post(user_tg_id, chat_id, mode)

    try:
        if hasattr(message.reply_to_message, 'message_id'):
            message_ids = list(range(message.reply_to_message.message_id - 1, message.message_id + 1))
            await bot_client.delete_messages(chat_id, message_ids)
        else:
            message_ids = message.message_id
            await bot_client.delete_messages(chat_id, message_ids)
    except Exception as err:
        logger.error(f'Ошибка при удалении поста из ленты пользователя: {err}')
    await send_post_to_support(viewed_post)


async def on_delete_post_button_click(callback: CallbackQuery):
    callback_pieces = callback.data.split(':')
    post_type = callback_pieces[1]
    post_id = int(callback_pieces[2])
    chat_id = callback.message.chat.id
    message = callback.message

    if post_type == ChannelPostTypes.PREMIUM:
        await delete_premium_channel_post(post_id)
    elif post_type == ChannelPostTypes.CATEGORY:
        await delete_category_channel_post(post_id)
    elif post_type == ChannelPostTypes.PERSONAL:
        await delete_user_channel_post(post_id)

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

    dp.register_message_handler(
        on_start_message,
        Text(equals=[general_reply_buttons_texts.START_BUTTON_TEXT]),
        state=[RecommendationsStates.RECOMMENDATIONS_FEED, CategoriesStates.CATEGORIES_FEED, PersonalStates.PERSONAL_FEED],
    )

    dp.register_message_handler(
        on_skip_message,
        Text(equals=general_reply_buttons_texts.SKIP_BUTTON_TEXT),
        state='*'
    )

    dp.register_message_handler(
        on_guide_command,
        commands=commands.GUIDE,
        state='*'
    )
