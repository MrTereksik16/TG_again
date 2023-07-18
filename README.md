## Описание правил кода для Leaf-бота

Ниже приведено описание правил кода для этого бота:

### Названия переменных

- Используйте стиль `snake_case` для названий переменных. Например: `user_id`, `message_text`, `channel_id`.

### Константы

- Константы следует выносить в отдельную папку `utils/consts` и писать их заглавными буквами с подчеркиваниями для разделения слов. Например: `MAX_ATTEMPTS`, `ADDED_CHANNELS_MESSAGE`.

### Названия обработчиков

- Названия обработчиков должны начинаться с префикса `on_`, за которым следует действие, на которое срабатывает обработчик. Например: `on_add_user_channels_message`, `on_delete_user_channels_command`. Это поможет ясно указать, к какому событию относится обработчик.

### Запросы к базе данных

- Запросы к базе данных следует писать в папке `database/queries`. При написании запросов начинайте название функции с типа запроса (`create`, `get`, `delete`, `update`). Обязательно оборачивайте запросы в блок `try-except-finally` и закрывайте сессию в блоке `finally`. Например:

```python
async def delete_personal_channel(username):
    from sqlalchemy import select
    from database.models import PersonalChannel, UserChannel, Session
    from config import logger

    session = Session()
    try:
        personal_channel_id =
        session.execute(select(PersonalChannel.id).where(PersonalChannel.username == username)).fetchone()[0]
        session.query(UserChannel).filter(UserChannel.channel_id == personal_channel_id).delete()
        session.flush()
        session.query(PersonalChannel).filter(PersonalChannel.id == personal_channel_id).delete()
        session.commit()
        return True
    except Exception as err:
        logger.error(f'Ошибка при удалении канала из списка пользователя: {err}')
        return False
    finally:
        session.close()
```

## Одинарные и двойные кавычки
- Мы используем одинарные кавычки для строковых литералов, за исключением случаев, когда внутри строки требуется использование одиночных кавычек. В таких случаях используйте двойные кавычки для обрамления строки. Например:

```python
message = 'Привет, пользователь!'
error_message = 'Произошла ошибка: "Неверный формат данных".'
```

## Соблюдение стандартов

- По возможности, следуйте стилю кода PEP 8. Или просто используйте форматирование Pycharm (```ctrl```+```alt```+```l```- Windows, ```⌥```+```⌘```+```L``` - MacOS)

## Обработка ошибок

- Включайте обработку ошибок в свой код, чтобы предотвратить сбои и обеспечить плавную работу бота (try-except-finally). 


**Правила в дальнейшем будут видоизменяться и дополняться. Все изменения в этом файле должны обговариваться!**
