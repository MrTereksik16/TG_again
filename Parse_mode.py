from aiogram import types
import Parse
from ORM import *
async def show_res(message: types.Message):
    pars_channels = await Parse.parse('Dota2')
    admin_users = []
    # if message.from_user.id not in admin_users:
    session.add(Personal_Channels(username='Dota2'))
    session.commit()



    # min_id_for_channel = wd.get_min_id_by_channel(data['name_channel'])
    # max_id_for_channel = wd.get_data(table='users', field_get='max_id_view_channel', fields_search=['user_tg_id'],
    #                      value=[message.from_user.id])[0]['max_id_view_channel']

    # max_id_for_channel = json.loads(max_id_for_channel)
    # max_id_for_channel[data['name_channel']] = min_id_for_channel
    # print(max_id_for_channel)
    # wd.change_data(table='users',field_change='max_id_view_channel', new_value=max_id_for_channel,field_parameter='user_tg_id', value_parameter=message.from_user.id)


