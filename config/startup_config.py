from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Посмотреть посты"),
        types.BotCommand("add_channels", "Добавить канал"),
        types.BotCommand("list", "Список добавленных каналов"),
        types.BotCommand("delete_channels", "Удалить каналы из списка"),
    ])
