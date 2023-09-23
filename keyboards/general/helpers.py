from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from utils.consts import callbacks
from database.models import PersonalPost, CategoryPost, PremiumPost
from keyboards.general.inline import general_inline_buttons_texts
from utils.custom_types import ChannelPostTypes, Feeds


def build_reply_buttons(texts: list[str | int]) -> list[KeyboardButton]:
    buttons = []
    for category in texts:
        buttons.append(KeyboardButton(text=category))
    return buttons


def build_reply_keyboard(buttons: list[KeyboardButton], n_cols: int = 2, header_buttons: list[KeyboardButton] | KeyboardButton = None,
                         footer_buttons: list = None) -> ReplyKeyboardMarkup:
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        if not isinstance(header_buttons, list):
            header_buttons = [header_buttons]
            menu.insert(0, header_buttons)
        else:
            header_buttons = reversed(header_buttons)
            for button in header_buttons:
                menu.insert(0, [button])

    if footer_buttons:
        menu.append(footer_buttons)
    return ReplyKeyboardMarkup(menu, resize_keyboard=True)


def build_reactions_inline_keyboard(
        likes: int, dislikes: int,
        post_type: ChannelPostTypes,
        post_id: int, feed: Feeds,
        next_button: InlineKeyboardButton = None
) -> InlineKeyboardMarkup:
    if likes >= 1000000:
        likes = f'{likes // 1000000}M'
    elif likes >= 1000:
        likes = f'{likes // 1000}K'

    if dislikes >= 1000000:
        likes = f'{dislikes // 1000000}M'
    elif dislikes >= 1000:
        dislikes = f'{dislikes // 1000}K'
    callback_data = f'{callbacks.LIKE}:{post_type}:{post_id}:{likes}:{dislikes}:{feed}'.encode()
    like_button = InlineKeyboardButton(f'{general_inline_buttons_texts.LIKE_BUTTON_TEXT} {likes}',
                                       callback_data=callback_data)

    callback_data = f'{callbacks.DISLIKE}:{post_type}:{post_id}:{likes}:{dislikes}:{feed}'.encode()
    dislike_button = InlineKeyboardButton(f'{general_inline_buttons_texts.DISLIKE_BUTTON_TEXT} {dislikes}',
                                          callback_data=callback_data)

    callback_data = f'{callbacks.REPORT}:{post_type}:{post_id}:{feed}'.encode()
    report_button = InlineKeyboardButton(general_inline_buttons_texts.REPORT_BUTTON_TEXT,
                                         callback_data=callback_data)
    if next_button:
        keyboard = InlineKeyboardMarkup([[like_button, dislike_button, report_button], [next_button]])
    else:
        keyboard = InlineKeyboardMarkup([[like_button, dislike_button, report_button]])

    return keyboard


def build_modes_inline_keyboard(user_mode: int, modes: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for mode in modes:
        button_text = mode['name']

        if user_mode == mode['id']:
            button_text += ' ✔'

        callback_data = f'{callbacks.MODES}:{mode["id"]}'
        mode_button = InlineKeyboardButton(button_text, callback_data=callback_data)
        buttons.append(mode_button)
    keyboard = InlineKeyboardMarkup([buttons])
    return keyboard


def build_delete_post_keyboard(post: PersonalPost | CategoryPost | PremiumPost, post_type: ChannelPostTypes) -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(general_inline_buttons_texts.DELETE_POST_BUTTON_TEXT,
                                  callback_data=f'{callbacks.DELETE_POST}:{post_type}:{post.id}')
    keyboard = InlineKeyboardMarkup([[button]])
    return keyboard
