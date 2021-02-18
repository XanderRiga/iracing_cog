import urllib.parse
from datetime import datetime
from pyracing.constants import Category
import os
import copy
from .models import Series
from .db_helpers import init_tortoise


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


def charset():
    return '<meta charset="UTF-8">\n'


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


async def are_valid_series(series_ids_to_check):
    """takes in a list of ids and returns true if they are
        all in the series list"""

    all_series = await Series.all()
    all_series_ids = list(map(lambda x: x.iracing_id, all_series))

    for entered_id in series_ids_to_check:
        if not await is_valid_series(entered_id, all_series_ids):
            return False

    return True


async def is_valid_series(series_id, all_series_ids):
    for existing_series_id in all_series_ids:
        if str(existing_series_id) == str(series_id):
            return True

    return False


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


def cleanup_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)


def six_months_before(date):
    month = date.month - 6
    year = date.year
    if month < 1:
        month += 12
        year = date.year - 1

    return datetime(year, month, date.day)


def peak_irating_value(iratings):
    max = iratings[0][1]
    for irating in iratings:
        if irating[1] > max:
            max = irating[1]

    return max


def is_home_guild(guild_id):
    return str(guild_id) == '174382936877957120' or \
           str(guild_id) == '286557202523750411'


def is_support_guild(guild_id):
    return str(guild_id) == '804743603464830976'
