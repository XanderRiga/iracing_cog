import urllib.parse
from datetime import datetime
from pyracing.constants import Category
from .storage import *


iracing_table_css = """#iracing_table {
                  font-family: Arial, Helvetica, sans-serif;
                  border-collapse: collapse;
                  width: 100%;
                }

                #iracing_table td, #iracing_table th {
                  border: 1px solid #ddd;
                  padding: 8px;
                }

                #iracing_table tr:nth-child(even){background-color: #f2f2f2;}

                #iracing_table th {
                  padding-top: 10px;
                  padding-bottom: 10px;
                  text-align: left;
                  background-color: #4CAF50;
                  color: white;
                }
                
                """

leaderboard_table_css = """#iracing_table {
                  font-family: Arial, Helvetica, sans-serif;
                  border-collapse: collapse;
                  width: 100%;
                }

                #iracing_table td, #iracing_table th {
                  border: 1px solid #ddd;
                  padding: 8px;
                }

                #iracing_table tr:nth-child(even){background-color: #f2f2f2;}

                #iracing_table th {
                  padding-top: 10px;
                  padding-bottom: 10px;
                  text-align: left;
                  background-color: #f40000;
                  color: white;
                }

                """

header_css = """
    #header {
      font-family: Arial, Helvetica, sans-serif;
    }
    
"""


def build_html_header_string(header_string):
    return f"<h2 id=\"header\" style=\"text-align:center\">{header_string}</h2>"


def wrap_in_style_tag(string):
    return '<style>' + string + '</style>'


def add_backticks(string):
    return '```' + string + '```'


def lowercase_to_readable_categories(category):
    if category == 'road':
        return 'Road'
    elif category == 'oval':
        return 'Oval'
    elif category == 'dirtroad':
        return 'Dirt Road'
    elif category == 'dirtoval':
        return 'Dirt Oval'


def category_id_from_string(string):
    if string == 'road':
        return Category.road.value
    if string == 'oval':
        return Category.oval.value
    if string == 'dirtroad':
        return Category.dirt_road.value
    if string == 'dirtoval':
        return Category.dirt_oval.value


def parse_encoded_string(string):
    return urllib.parse.unquote(string).replace('+', ' ')


def get_current_year_stats(yearly_stats_list):
    """This takes the massive list of a user's yearly stats dicts
    and returns just the yearly stats from the current year"""
    current_year = str(datetime.now().year)
    return filter(lambda x: x['year'] == current_year, yearly_stats_list)


def minutes_since_last_update(guild_id, log):
    try:
        last_update = get_last_update_datetime(guild_id)
        if not last_update:
            return None
        return round((datetime.now() - last_update).seconds / 60, 1)
    except Exception as e:
        log.warning('datetime parsing exploded')
        log.warning(e)
        return None


def get_relevant_leaderboard_data(guild_dict, category):
    if category == 'road':
        valid_guild_dict = dict(filter(
            lambda x: 'road_irating' in x[1],
            guild_dict.items()
        ))
        return sorted(valid_guild_dict.items(), key=lambda x: int(x[1]['road_irating'][-1][1]), reverse=True)
    elif category == 'oval':
        valid_guild_dict = dict(filter(
            lambda x: 'oval_irating' in x[1],
            guild_dict.items()
        ))
        return sorted(valid_guild_dict.items(), key=lambda x: int(x[1]['oval_irating'][-1][1]), reverse=True)
    elif category == 'dirtroad':
        valid_guild_dict = dict(filter(
            lambda x: 'dirt_road_irating' in x[1],
            guild_dict.items()
        ))
        return sorted(valid_guild_dict.items(), key=lambda x: int(x[1]['dirt_road_irating'][-1][1]), reverse=True)
    elif category == 'dirtoval':
        valid_guild_dict = dict(filter(
            lambda x: 'dirt_oval_irating' in x[1],
            guild_dict.items()
        ))
        return sorted(valid_guild_dict.items(), key=lambda x: int(x[1]['dirt_oval_irating'][-1][1]), reverse=True)

    return []


def delete_missing_users(guild):
    guild_dict = get_guild_dict(guild.id)
    current_member_ids = list(map(lambda x: x.id, guild.members))
    for user_id in get_user_ids(guild.id):
        if int(user_id) not in current_member_ids:
            guild_dict.pop(user_id, None)

    set_guild_data(guild.id, guild_dict)


def get_series_name(all_series, series_id):
    for series in all_series:
        if str(series.series_id) == str(series_id):
            # We want to truncate the series name to 35 because some of them are massive
            return series.series_name_short[:33] + '..' if len(
                series.series_name_short) > 35 else series.series_name_short

    return "Unknown Series"


def build_embeds(discord, series, name):
    embeds = [discord.Embed(title=name)]
    embed_index = 0

    for i, season in enumerate(series):
        print(str(len(embeds[embed_index])))
        print(embed_index)
        if len(embeds[embed_index]) >= 500:
            embed_index += 1
            embeds.append(discord.Embed())
        embeds[embed_index].add_field(name=str(season.series_id), value=season.series_name_short)

    return embeds


def ids_valid_series(series, ids):
    """takes in a list of ids and returns true if they are
        all in the series list"""
    for series_id in ids:
        if not any(x.series_id == series_id for x in series):
            return False

    return True


def series_from_ids(ids, all_series):
    series = []
    for id in ids:
        series.append(serie_from_id(id, all_series))

    return series


def serie_from_id(id, all_series):
    for serie in all_series:
        if id == serie.series_id:
            return serie

    return None
