from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ChatActions, InputFile, ContentType
from aiogram import Dispatcher

from create_bot import bot

from buttons.reply.reply_buttons_text import *
from database.queries.create_queries import *
from database.queries.delete_queries import *
from handlers.general_handlers import on_start_message

from store.states import UserStates


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
    # dp.register_message_handler(
    #     send_post_for_user_in_personal_feed,
    #     Text(equals=SKIP_BUTTON_TEXT),
    #     state=UserStates.CATEGORIES_FEED
    # )

    dp.register_message_handler(
        on_categories_message,
        content_types=ContentType.TEXT,
        state=UserStates.GET_USER_CATEGORIES
    )
