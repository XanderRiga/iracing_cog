from datetime import datetime
import json
import os

folder = './data/'
datetime_format = '%Y-%m-%d %H:%M:%S'


def store_iratings(user_id, guild_id, iratings):
    ensure_file_exists(guild_id)
    user_data = get_user_dict(user_id, guild_id)

    user_data['oval_irating'] = iratings['oval']
    user_data['road_irating'] = iratings['road']
    user_data['dirt_road_irating'] = iratings['dirt']
    user_data['dirt_oval_irating'] = iratings['dirtoval']

    set_user_data(user_id, guild_id, user_data)


def store_license_classes(user_id, guild_id, license_classes):
    ensure_file_exists(guild_id)
    user_data = get_user_dict(user_id, guild_id)

    user_data['oval_license_class'] = license_classes['oval']
    user_data['road_license_class'] = license_classes['road']
    user_data['dirt_road_license_class'] = license_classes['dirt']
    user_data['dirt_oval_license_class'] = license_classes['dirtoval']

    set_user_data(user_id, guild_id, user_data)


def save_iracing_id(user_id, guild_id, iracing_id):
    ensure_file_exists(guild_id)

    # We want to override any data saved here because this is a new ID
    user_data = {'iracing_id': iracing_id}

    set_user_data(user_id, guild_id, user_data)


def update_user(user_id, guild_id, career_stats_list, yearly_stats_list, recent_races_stats_list):
    ensure_file_exists(guild_id)

    user_data = get_user_dict(user_id, guild_id)

    if career_stats_list:
        career_stats_dict_list = list(map(lambda x: x.__dict__, career_stats_list))
        user_data['career_stats'] = career_stats_dict_list

    if yearly_stats_list:
        yearly_stats_dict_list = list(map(lambda x: x.__dict__, yearly_stats_list))
        user_data['yearly_stats'] = yearly_stats_dict_list

    if recent_races_stats_list:
        recent_races_stats_dict_list = list(map(lambda x: x.__dict__, recent_races_stats_list))
        user_data['recent_races'] = recent_races_stats_dict_list

    set_user_data(user_id, guild_id, user_data)


def set_guild_data(guild_id, guild_dict):
    guild_dict['last_update'] = datetime.now().strftime(datetime_format)
    with open(file_path(guild_id), 'w') as file:
        json.dump(guild_dict, file)


def set_guild_favorites(guild_id, favorites):
    guild_dict = get_guild_dict(guild_id)
    guild_dict['favorites'] = favorites
    with open(file_path(guild_id), 'w') as file:
        json.dump(guild_dict, file)


def get_guild_favorites(guild_id):
    guild_dict = get_guild_dict(guild_id)
    if 'favorites' in guild_dict.keys():
        return guild_dict['favorites']
    else:
        return {}


def set_user_data(user_id, guild_id, user_data):
    ensure_file_exists(guild_id)

    full_dict = get_guild_dict(guild_id)
    full_dict[user_id] = user_data

    with open(file_path(guild_id), 'w') as file:
        json.dump(full_dict, file)


def get_guild_dict(guild_id):
    ensure_file_exists(guild_id)

    with open(file_path(guild_id), 'r') as file:
        return json.load(file)


def get_user_dict(user_id, guild_id):
    dictionary = get_guild_dict(guild_id)

    if user_id in dictionary:
        return dictionary[user_id]
    else:
        return {}


def get_user_ids(guild_id):
    ensure_file_exists(guild_id)

    with open(file_path(guild_id), 'r') as file:
        guild_json = json.load(file)

    ids = []
    for key in guild_json:
        if key not in ['last_update', 'favorites']:
            ids.append(key)

    return ids


def get_user_iracing_id(user_id, guild_id):
    user_data = get_user_dict(user_id, guild_id)

    if not user_data or 'iracing_id' not in user_data:
        return None

    return user_data['iracing_id']


def get_user_iratings(user_id, guild_id, category):
    try:
        user_data = get_user_dict(user_id, guild_id)
        return user_data[f'{category}_irating']
    except:
        return []


def get_last_update_datetime(guild_id):
    guild_dict = get_guild_dict(guild_id)
    if not guild_dict.get('last_update'):
        return None

    return datetime.strptime(guild_dict.get('last_update'), datetime_format)


def ensure_file_exists(guild_id):
    ensure_folder_exists()
    path = file_path(guild_id)
    if os.path.exists(path):
        return
    else:
        with open(path, 'w') as file:
            json.dump({}, file)


def ensure_folder_exists():
    if os.path.exists(folder):
        return
    else:
        os.mkdir(folder)


def file_path(guild_id):
    return folder + str(guild_id) + '.json'
