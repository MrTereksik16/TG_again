import time
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType
from pyrogram.types import InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from create_bot import bot_client
from database.queries.delete_queries import delete_category, delete_premium_channel, delete_category_channel, delete_coefficient
from database.queries.get_queries import get_categories, get_all_premium_channels, get_all_categories_channels, get_coefficients, get_statistic
from database.queries.create_queries import create_premium_posts, create_category_posts, create_category, create_coefficient
from database.queries.update_queries import update_category
from keyboards.general.helpers import build_reply_buttons, build_reply_keyboard
from utils.consts import answers, errors, callbacks
from parse import parse
from store.states import AdminPanelStates
from utils.helpers import add_channels, convert_list_of_items_to_string, reset_and_switch_state, remove_file_or_folder
from keyboards import admin_inline_keyboards, admin_reply_buttons_texts, admin_reply_keyboards, general_reply_keyboards, general_reply_buttons_texts, \
    general_reply_buttons
from utils.custom_types import ChannelPostTypes
from config import config
from config.logging_config import logger


async def on_add_premium_channels_message(message: Message, state: FSMContext):
    coefficients = await get_coefficients()
    if not coefficients:
        return await message.answer('Список коэффициентов пуст. <b>Добавьте минимум один коэффициент</b>')

    await state.set_state(AdminPanelStates.GET_CHANNELS_COEFFICIENT)
    await state.update_data(coefficients=coefficients)
    buttons = build_reply_buttons(coefficients)
    keyboard = build_reply_keyboard(buttons, n_cols=1, header_buttons=general_reply_buttons.cancel_button)
    await message.answer('<b>Выберите коэффициент</b>\n\nОн влияет на частоту попадания постов из каналов в <b>рекомендации</b>',
                         reply_markup=keyboard)


async def on_channels_coefficient_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    coefficients: list = (await state.get_data())['coefficients']
    coefficient = message.text

    if coefficient not in coefficients:
        return await message.answer('Такого коэффициента нет')

    await state.set_state(AdminPanelStates.GET_PREMIUM_CHANNELS)
    await state.update_data(coefficient=coefficient[:1])
    await message.answer(answers.ADD_CHANNELS_MESSAGE_TEXT, reply_markup=general_reply_keyboards.general_cancel_keyboard)


async def on_premium_channels_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    coefficient = (await state.get_data())['coefficient']
    keyboard = admin_reply_keyboards.admin_panel_control_keyboard
    chat_id = message.chat.id
    channel_type = ChannelPostTypes.PREMIUM
    channels = message.text
    user_tg_id = message.from_user.id

    result_data = await add_channels(channels, channel_type=channel_type, user_tg_id=user_tg_id, coefficient=coefficient)

    answer = result_data.answer
    to_parse = result_data.to_parse
    await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)

    if not to_parse:
        return await message.answer(answer, reply_markup=keyboard)
    else:
        keyboard = ReplyKeyboardRemove()
        await message.answer(answer, reply_markup=keyboard)

    to_parse_len = len(to_parse)
    for i, channel_username in enumerate(to_parse, start=1):
        await delete_category_channel(channel_username)
        posts = await parse(channel_username, chat_id=chat_id, channel_type=channel_type)
        if posts == errors.NO_POSTS:
            await bot_client.send_message(chat_id, 'Канал пуст', reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
        else:
            if i == to_parse_len:
                keyboard = admin_reply_keyboards.admin_panel_control_keyboard
            result = await create_premium_posts(posts)
            if result:
                await bot_client.send_message(chat_id, f'Посты с канала @{channel_username} получены 👍', reply_markup=keyboard)
            else:
                await bot_client.send_message(chat_id, f'Не удалось получить посты с канала @{channel_username}', reply_markup=keyboard)
        time.sleep(0.8)


async def on_add_category_channels_message(message: Message, state: FSMContext):
    categories = await get_categories()
    if not categories:
        return await message.answer('Список категорий пуст', reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    answer = '<b>Выберите категорию</b>'
    buttons = build_reply_buttons(categories)
    keyboard = build_reply_keyboard(buttons, header_buttons=general_reply_buttons.cancel_button)

    await message.answer(answer, reply_markup=keyboard)
    await state.update_data(categories=categories)
    await state.set_state(AdminPanelStates.GET_CHANNELS_CATEGORY)


async def on_category_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    context = await state.get_data()
    categories = context['categories']
    if message.text not in categories:
        return await message.answer('Такой категории нет')
    category = message.text.split(' ')[0]
    await state.update_data(category=category)
    await state.set_state(AdminPanelStates.GET_CATEGORY_CHANNELS)
    await message.answer(text=answers.ADD_CHANNELS_MESSAGE_TEXT, reply_markup=general_reply_keyboards.general_cancel_keyboard)


async def on_category_channels_message(message: Message, state: FSMContext):
    keyboard = admin_reply_keyboards.admin_panel_control_keyboard
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=keyboard)

    chat_id = message.chat.id
    channel_type = ChannelPostTypes.CATEGORY
    category = (await state.get_data())['category']
    channels = message.text
    user_tg_id = message.from_user.id

    result = await add_channels(channels, channel_type=channel_type, user_tg_id=user_tg_id, category_name=category)

    answer = result.answer
    to_parse = result.to_parse

    await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)

    if not to_parse:
        return await message.answer(answer, reply_markup=keyboard)
    else:
        keyboard = ReplyKeyboardRemove()
        await message.answer(answer, reply_markup=keyboard)

    to_parse_len = len(to_parse)
    for i, channel_username in enumerate(to_parse, start=1):
        await delete_premium_channel(channel_username)
        posts = await parse(channel_username, chat_id=chat_id, channel_type=channel_type)

        if posts == errors.NO_POSTS:
            await bot_client.send_message(chat_id, 'Канал пуст', reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
        else:
            if i == to_parse_len:
                keyboard = admin_reply_keyboards.admin_panel_control_keyboard

            result = await create_category_posts(posts)
            if result:
                await bot_client.send_message(chat_id, f'Посты с канала @{channel_username} получены 👍', reply_markup=keyboard)
            else:
                await bot_client.send_message(chat_id, f'Не удалось получить посты с канала @{channel_username}', reply_markup=keyboard)
        time.sleep(0.8)


async def on_list_premium_channels_message(message: Message):
    channels = await get_all_premium_channels()
    channels = [f'@{channel.channel_username} | <b>{channel.coefficient}</b>' for channel in channels]
    answer = convert_list_of_items_to_string(channels, code=False)

    if not channels:
        answer = 'Список премиальных каналов пуст'

    await message.answer(answer)


async def on_list_categories_message(message: Message):
    categories = await get_categories()
    answer = convert_list_of_items_to_string(categories)

    if not categories:
        answer = 'Список категорий пуст'

    await message.answer(answer)


async def on_list_categories_channels_message(message: Message):
    categories_channels = await get_all_categories_channels()
    if not categories_channels:
        return await message.answer('Список каналов из категорий пуст')
    else:
        categories_channels = [f'@{channel.channel_username} | <code>{channel.name} {channel.emoji}</code>' for channel in categories_channels]
        answer = convert_list_of_items_to_string(categories_channels, code=False)
        await message.answer(answer)


async def on_add_category_message(message: Message, state: FSMContext):
    keyboard = general_reply_keyboards.general_cancel_keyboard
    await message.answer('<b>Введите название категории</b>', reply_markup=keyboard)
    await state.set_state(AdminPanelStates.GET_CATEGORY_NAME)


async def on_add_category_name_message(message: Message, state: FSMContext):
    keyboard = general_reply_keyboards.general_cancel_keyboard
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    await state.update_data(category_name=message.text)
    await message.answer('<b>Введите эмодзи</b>', reply_markup=keyboard)
    await state.set_state(AdminPanelStates.GET_CATEGORY_EMOJI)


async def on_add_category_emoji_message(message: Message, state: FSMContext):
    keyboard = admin_reply_keyboards.admin_panel_control_keyboard

    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=keyboard)

    category_name = (await state.get_data())['category_name']
    category_emoji = message.text
    result = await create_category(category_name, category_emoji)

    if result == errors.DUPLICATE_ERROR_TEXT:
        await message.answer('Категория с таким названием уже есть', reply_markup=keyboard)
    elif result:
        await message.answer(f'Категория {category_name} {category_emoji} успешно добавлена!', reply_markup=keyboard)
    else:
        await message.answer('Не удалось добавить категорию', reply_markup=keyboard)

    await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)


async def on_delete_category_message(message: Message, state: FSMContext):
    categories = await get_categories()
    if not categories:
        return await message.answer('Список категорий пуст')

    buttons = build_reply_buttons(categories)
    keyboard = build_reply_keyboard(buttons, header_buttons=general_reply_buttons.cancel_button)
    await message.answer(
        'Нажмите на категорию, которую хотите удалить.\n\n<b>Если добавленные в категории каналы относятся к выбранной категории, то они также удалятся!</b>',
        reply_markup=keyboard)
    await state.update_data(categories=categories)
    await state.set_state(AdminPanelStates.DELETE_CATEGORIES)


async def on_delete_category_name_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    categories: list = (await state.get_data())['categories']

    if message.text not in categories:
        return await message.answer('Такой категории нет')

    category = message.text
    category_name = message.text.split(' ')[0]
    result = await delete_category(category_name)

    if result:
        categories.remove(category)
        if not categories:
            await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
            return await message.answer('Список категорий пуст', reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
        buttons = build_reply_buttons(categories)
        keyboard = build_reply_keyboard(buttons, header_buttons=general_reply_buttons.cancel_button)
        await message.answer('Категория успешно удалена', reply_markup=keyboard)
        await state.update_data(categories=categories)
    else:
        await message.answer('Не удалось удалить категорию')


async def on_delete_premium_channels_message(message: Message, state: FSMContext):
    premium_channels = await get_all_premium_channels()
    if not premium_channels:
        return await message.answer('Список премиальных каналов пуст')

    channels = [f'{channel.channel_username}:{channel.coefficient}' for channel in premium_channels]
    buttons = []
    for channel in channels:
        callback_data = f'{callbacks.DELETE_PREMIUM_CHANNEL}:{channel}'
        buttons.append([InlineKeyboardButton(channel.replace(':', ' | '), callback_data=callback_data)])

    keyboard = InlineKeyboardMarkup(buttons)
    msg = await message.answer(answers.DELETE_CHANNEL_MESSAGE_TEXT, reply_markup=keyboard)
    await state.update_data(premium_channels=channels, delete_premium_channels_message=msg)


async def on_delete_premium_button_click(callback: CallbackQuery, state: FSMContext):
    context_data = await state.get_data()
    premium_channels = context_data['premium_channels']
    message = context_data['delete_premium_channels_message']

    callback_pieces = callback.data.split(':')[1:]
    channel = ':'.join(callback_pieces)
    channel_username = callback_pieces[0]

    try:
        premium_channels.remove(channel)
    except ValueError:
        return await callback.answer('Канал уже удалён')

    result = await delete_premium_channel(channel_username)

    await state.update_data(premium_channels=premium_channels)
    buttons = []
    for channel in premium_channels:
        callback_data = f'{callbacks.DELETE_PREMIUM_CHANNEL}:{channel}'
        buttons.append([InlineKeyboardButton(channel.replace(':', ' | '), callback_data=callback_data)])
    keyboard = InlineKeyboardMarkup(buttons)

    if not buttons:
        await message.edit_text('Список премиальных каналов пуст')
    else:
        await message.edit_reply_markup(reply_markup=keyboard)

    if result:
        remove_file_or_folder(config.MEDIA_DIR + channel_username)
        await callback.answer('Канал успешно удалён')


async def on_delete_categories_channels_message(message: Message, state: FSMContext):
    channels_list = await get_all_categories_channels()
    if not channels_list:
        return await message.answer('Список каналов из категорий пуст')

    buttons_texts = [f'{channel.channel_username} | {channel.name} {channel.emoji}' for channel in channels_list]
    buttons = build_reply_buttons(buttons_texts)
    keyboard = build_reply_keyboard(buttons, header_buttons=general_reply_buttons.cancel_button)

    await message.answer(answers.DELETE_CHANNEL_MESSAGE_TEXT, reply_markup=keyboard)
    await state.update_data(buttons_texts=buttons_texts)
    await state.set_state(AdminPanelStates.DELETE_CATEGORIES_CHANNELS)


async def on_category_channel_message(message: Message, state: FSMContext):
    keyboard = admin_reply_keyboards.admin_panel_control_keyboard
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=keyboard)

    buttons_texts: list = (await state.get_data())['buttons_texts']

    if message.text in buttons_texts:
        channel_username = message.text.split(' | ')[0]
        result = await delete_category_channel(channel_username)
        if result:
            remove_file_or_folder(config.MEDIA_DIR + channel_username)
            buttons_texts.remove(message.text)
            if not buttons_texts:
                await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
                return await message.answer('Все каналы из категорий удалены', reply_markup=keyboard)

            buttons = build_reply_buttons(buttons_texts)
            keyboard = build_reply_keyboard(buttons, header_buttons=general_reply_buttons.cancel_button)
            await message.answer('Канал успешно удалён', reply_markup=keyboard)
            await state.update_data(buttons_texts=buttons_texts)
        else:
            await message.answer('Не удалось удалить канал')
    else:
        await message.answer('Такого канала нет в списке')


async def on_add_coefficients_message(message: Message, state: FSMContext):
    await state.set_state(AdminPanelStates.GET_COEFFICIENTS)
    await message.answer('<b>Введите через запятую целочисленные значения новых коэффициентов. Коэффициент не должен быть меньше 2</b>',
                         reply_markup=general_reply_keyboards.general_cancel_keyboard)


async def on_coefficients_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await state.set_state(AdminPanelStates.ADMIN_PANEL)
        await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    added = []
    not_added = []
    already_added = []
    coefficients = message.text.split(',')

    for coefficient in coefficients:
        try:
            coefficient_value = int(coefficient)
            result = await create_coefficient(coefficient_value)
            if result == errors.DUPLICATE_ERROR_TEXT:
                already_added.append(coefficient)
            elif result:
                added.append(coefficient)
        except ValueError:
            not_added.append(coefficient)
    answer = ''
    if added:
        answer += 'Добавлены коэффициенты: ' + ','.join(added) + '\n'

    if already_added:
        answer += 'Ранее добавленные коэффициенты: ' + ','.join(already_added) + '\n'

    if not_added:
        answer += 'Не добавлены коэффициенты: ' + ','.join(not_added) + '\n'

    await state.set_state(AdminPanelStates.ADMIN_PANEL)
    await message.answer(answer, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)


async def on_list_coefficients_message(message: Message):
    coefficients = await get_coefficients()
    if not coefficients:
        await message.answer('Список коэффициентов пуст')

    answer = convert_list_of_items_to_string(coefficients)
    await message.answer(answer)


async def on_delete_coefficients_message(message: Message, state: FSMContext):
    coefficients = await get_coefficients()
    if not coefficients:
        return await message.answer('Список коэффициентов пуст')
    buttons = []
    for coefficient in coefficients:
        callback_data = f'{callbacks.DELETE_COEFFICIENT}:{coefficient}'
        buttons.append([InlineKeyboardButton(coefficient, callback_data=callback_data)])
    keyboard = InlineKeyboardMarkup(buttons)

    msg = await message.answer('Нажмите на коэффициент, который хотите удалить', reply_markup=keyboard)
    await state.update_data(coefficients=coefficients, delete_coefficients_message=msg)


async def on_delete_coefficient_button_click(callback: CallbackQuery, state: FSMContext):
    context_data = await state.get_data()
    coefficients = context_data['coefficients']
    message = context_data['delete_coefficients_message']

    callback_pieces = callback.data.split(':')[1:]
    coefficient = int(callback_pieces[0].replace('X', ''))

    try:
        coefficients.remove(f'{coefficient}X')
    except ValueError:
        return await callback.answer('Коэффициент уже удалён')

    result = await delete_coefficient(coefficient)
    await state.update_data(coefficients=coefficients)
    buttons = []
    for coefficient in coefficients:
        callback_data = f'{callbacks.DELETE_COEFFICIENT}:{coefficient}'
        buttons.append([InlineKeyboardButton(coefficient, callback_data=callback_data)])
    keyboard = InlineKeyboardMarkup(buttons)

    if not buttons:
        await message.edit_text('Список коэффициентов пуст')
    else:
        await message.edit_reply_markup(reply_markup=keyboard)

    if result:
        await callback.answer('Коэффициент успешно удалён')


async def on_list_statistic_message(message: Message, state: FSMContext):
    statistic = await get_statistic()
    answer = f'<i>Всего пользователей</i>: {statistic.total_users}\n<i>Новых пользователей</i>: {statistic.user_growth} 🆕\n<i>Пользовались сегодня</i>: {statistic.daily_users} 🔥\n<i>Лайков за сегодня</i>: {statistic.daily_likes} ❤\n<i>Дизлайков за сегодня</i>: {statistic.daily_dislikes} 👎\n'
    await message.answer(answer, reply_markup=admin_inline_keyboards.admin_recent_keyboard)
    await state.update_data(statistic=answer)


async def on_forward_statistic_button_click(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    await bot_client.send_message(chat_id,
                                  'Введите <b>ссылку в формате @имя_пользователя</b> получателя статистики',
                                  reply_markup=general_reply_keyboards.general_cancel_keyboard)
    await state.set_state(AdminPanelStates.GET_PHONE_NUMBER)
    await callback.answer()


async def on_receiver_phone_number_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await state.set_state(AdminPanelStates.ADMIN_PANEL)
        await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    bot = await bot_client.get_me()
    answer = f'<b>Статистика {bot.first_name}</b>:\n\n'
    answer += f'{(await state.get_data())["statistic"]}\n\n'
    # answer += f'{answers.RATES_MESSAGE_TEXT}'

    try:
        await bot_client.send_message(message.text, answer)
        await message.answer('Статистика отправлена', reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    except Exception as err:
        logger.error(f'Ошибка при отправлении статистики:{err}')
        await message.answer('Неверная или несуществующая ссылка пользователя')


async def on_rename_category_message(message: Message, state: FSMContext):
    categories = await get_categories()
    if not categories:
        return await message.answer('Список категорий пуст')

    buttons = build_reply_buttons(categories)
    keyboard = build_reply_keyboard(buttons, header_buttons=general_reply_buttons.cancel_button)
    await message.answer('Нажмите на категорию, которую хотите переименовать.', reply_markup=keyboard)
    await state.update_data(categories=categories)
    await state.set_state(AdminPanelStates.RENAME_CATEGORY)


async def on_rename_category_name_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)

    categories: list = (await state.get_data())['categories']

    if message.text not in categories:
        return await message.answer('Такой категории нет')

    old_category_name = message.text.split(' ')[0]
    await state.update_data(old_category_name=old_category_name)
    await state.set_state(AdminPanelStates.GET_NEW_CATEGORY_NAME)
    await message.answer('Введите новое <b>название</b> категории. Если вы хотите изменить и эмодзи категории, то просто напиши её через пробел',
                         reply_markup=general_reply_keyboards.general_cancel_keyboard)


async def on_new_category_message(message: Message, state: FSMContext):
    if message.text == general_reply_buttons_texts.CANCEL_BUTTON_TEXT:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        return await message.answer(answers.ADMIN_PANEL_MESSAGE_TEXT, reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    old_category_name = (await state.get_data())['old_category_name']

    new_category = message.text.split(' ')
    new_category_name = new_category[0]
    new_category_emoji = None

    if len(new_category) > 1:
        new_category_emoji = new_category[1]

    result = await update_category(old_category_name, new_category_name, new_category_emoji)

    if result:
        await reset_and_switch_state(state, AdminPanelStates.ADMIN_PANEL)
        await message.answer('Название категории успешно изменено', reply_markup=admin_reply_keyboards.admin_panel_control_keyboard)
    else:
        await message.answer('Не удалось обновить название категории')


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(
        on_add_premium_channels_message,
        Text(equals=admin_reply_buttons_texts.ADD_PREMIUM_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )
    dp.register_message_handler(
        on_channels_coefficient_message,
        content_types=ContentType.TEXT,
        state=AdminPanelStates.GET_CHANNELS_COEFFICIENT
    )
    dp.register_message_handler(
        on_premium_channels_message,
        state=AdminPanelStates.GET_PREMIUM_CHANNELS
    )

    dp.register_message_handler(
        on_add_category_channels_message,
        Text(equals=admin_reply_buttons_texts.ADD_CATEGORY_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_category_message,
        state=AdminPanelStates.GET_CHANNELS_CATEGORY
    )

    dp.register_message_handler(
        on_category_channels_message,
        state=AdminPanelStates.GET_CATEGORY_CHANNELS
    )

    dp.register_message_handler(
        on_list_premium_channels_message,
        Text(equals=admin_reply_buttons_texts.LIST_PREMIUM_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_list_categories_message,
        Text(equals=admin_reply_buttons_texts.LIST_CATEGORIES_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_list_categories_channels_message,
        Text(equals=admin_reply_buttons_texts.LIST_CATEGORIES_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_add_category_message,
        Text(admin_reply_buttons_texts.ADD_CATEGORY_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_add_category_name_message,
        content_types=ContentType.TEXT,
        state=AdminPanelStates.GET_CATEGORY_NAME
    )

    dp.register_message_handler(
        on_add_category_emoji_message,
        content_types=ContentType.TEXT,
        state=AdminPanelStates.GET_CATEGORY_EMOJI
    )

    dp.register_message_handler(
        on_delete_category_message,
        Text(equals=admin_reply_buttons_texts.DELETE_CATEGORY_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_delete_category_name_message,
        content_types=ContentType.TEXT,
        state=AdminPanelStates.DELETE_CATEGORIES
    )

    dp.register_message_handler(
        on_delete_premium_channels_message,
        Text(equals=admin_reply_buttons_texts.DELETE_PREMIUM_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_callback_query_handler(
        on_delete_premium_button_click,
        Text(startswith=callbacks.DELETE_PREMIUM_CHANNEL),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_delete_categories_channels_message,
        Text(admin_reply_buttons_texts.DELETE_CATEGORIES_CHANNELS_BUTTON_TEXT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_category_channel_message,
        content_types=ContentType.TEXT,
        state=AdminPanelStates.DELETE_CATEGORIES_CHANNELS
    )

    dp.register_message_handler(
        on_add_coefficients_message,
        Text(admin_reply_buttons_texts.ADD_COEFFICIENTS),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_coefficients_message,
        content_types=ContentType.TEXT,
        state=AdminPanelStates.GET_COEFFICIENTS
    )

    dp.register_message_handler(
        on_delete_coefficients_message,
        Text(admin_reply_buttons_texts.DELETE_COEFFICIENTS),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_callback_query_handler(
        on_delete_coefficient_button_click,
        Text(startswith=callbacks.DELETE_COEFFICIENT),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_list_coefficients_message,
        Text(admin_reply_buttons_texts.LIST_COEFFICIENTS),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_list_statistic_message,
        Text(admin_reply_buttons_texts.LIST_STATISTIC),
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_callback_query_handler(
        on_forward_statistic_button_click,
        Text(callbacks.FORWARD),
        state='*'
    )

    dp.register_message_handler(
        on_receiver_phone_number_message,
        state=AdminPanelStates.GET_PHONE_NUMBER
    )

    dp.register_message_handler(
        on_rename_category_message,
        state=AdminPanelStates.ADMIN_PANEL
    )

    dp.register_message_handler(
        on_rename_category_name_message,
        state=AdminPanelStates.RENAME_CATEGORY
    )

    dp.register_message_handler(
        on_new_category_message,
        state=AdminPanelStates.GET_NEW_CATEGORY_NAME
    )
