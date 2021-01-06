from .helpers import *
from prettytable import PrettyTable
import discord


def get_yearly_stats_html(yearly_stats, iracing_id):
    table = PrettyTable()
    table.field_names = [
        'Year', 'Category', 'Starts', 'Top 5s', 'Wins', 'Avg Start',
        'Avg Finish', 'Avg Incidents', 'Top 5 %', 'Win %'
    ]

    for yearly_stat in yearly_stats:
        table.add_row(
            [
                str(yearly_stat.year),
                yearly_stat.category,
                str(yearly_stat.starts),
                str(yearly_stat.top_5s),
                str(yearly_stat.wins),
                str(yearly_stat.pos_start_avg),
                str(yearly_stat.pos_finish_avg),
                str(yearly_stat.incidents_avg),
                str(yearly_stat.top_5_pcnt) + '%',
                str(yearly_stat.win_pcnt) + '%'
            ]
        )

    header_html_string = build_html_header_string(f'Yearly Stats for user: {iracing_id}')
    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    css = wrap_in_style_tag(iracing_table_css + header_css)

    return css + header_html_string + "\n" + html_string


def get_leaderboard_html_string(user_data_list, guild, category, log, yearly=False):
    type_string = 'Yearly' if yearly else 'Career'
    minutes_since_update = minutes_since_last_update(guild.id, log)
    time_since_update_string = f' - Last updated {minutes_since_update} minute(s) ago' if minutes_since_update else ''
    header_string = 'iRacing ' + lowercase_to_readable_categories(category) + ' ' + \
                    type_string + ' Leaderboard' + time_since_update_string

    table = PrettyTable()
    table.field_names = [
        '#', 'Discord Name', 'iRacing Name', 'Starts', 'iRating', 'License', 'Wins', 'Top 5s',
        'Laps Led', 'Win %', 'Top 5 %', 'Laps Led %', 'Avg Incidents'
    ]

    for index, item in enumerate(user_data_list, start=1):
        try:
            member = discord.utils.find(lambda m: m.id == int(item[0]), guild.members)
            if member:
                member_name = member.name
            else:
                print('Could not find user for id: ' + str(item[0]))
                member_name = ''

            if yearly:
                stats_list = get_current_year_stats(item[-1]['yearly_stats'])
            else:
                stats_list = item[-1]['career_stats']

            irating = 0
            if category == 'road':
                irating = item[-1]['road_irating'][-1][1]
            elif category == 'oval':
                irating = item[-1]['oval_irating'][-1][1]
            elif category == 'dirtroad':
                irating = item[-1]['dirt_road_irating'][-1][1]
            elif category == 'dirtoval':
                irating = item[-1]['dirt_oval_irating'][-1][1]

            license_class = 'N/A'
            if category == 'road':
                license_class = item[-1]['road_license_class']
            elif category == 'oval':
                license_class = item[-1]['oval_license_class']
            elif category == 'dirtroad':
                license_class = item[-1]['dirt_road_license_class']
            elif category == 'dirtoval':
                license_class = item[-1]['dirt_oval_license_class']

            iracing_name = ''
            if 'name' in item[-1]:
                iracing_name = item[-1]['name']

            career_stats = None
            for stat in stats_list:
                if category == 'road':
                    if stat['category'] == 'Road':
                        career_stats = stat
                elif category == 'oval':
                    if stat['category'] == 'Oval':
                        career_stats = stat
                elif category == 'dirtroad':
                    if stat['category'] == 'Dirt Road':
                        career_stats = stat
                elif category == 'dirtoval':
                    if stat['category'] == 'Dirt Oval':
                        career_stats = stat

            if career_stats:
                table.add_row(
                    [
                        index,
                        member_name,
                        iracing_name,
                        str(career_stats['starts']),
                        str(irating),
                        str(license_class),
                        str(career_stats['wins']),
                        str(career_stats['top_5s']),
                        str(career_stats['laps_led']),
                        str(career_stats['win_pcnt']) + '%',
                        str(career_stats['top_5_pcnt']) + '%',
                        str(career_stats['laps_led_pcnt']) + '%',
                        str(career_stats['incidents_avg']),
                    ]
                )
        except Exception as e:
            log.error(e)
            log.error(f'Error printing leaderboard data for user: {item}')
            continue

    header_html_string = build_html_header_string(header_string)
    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    css = wrap_in_style_tag(leaderboard_table_css + header_css)

    return css + header_html_string + "\n" + html_string


def get_career_stats_html(career_stats, iracing_id):
    table = PrettyTable()
    table.field_names = [
        'Category', 'Starts', 'Top 5s', 'Wins', 'Avg Start', 'Avg Finish', 'Avg Incidents', 'Top 5 %', 'Win %'
    ]
    for career_stat in career_stats:
        table.add_row(
            [
                career_stat.category,
                str(career_stat.starts),
                str(career_stat.top_5s),
                str(career_stat.wins),
                str(career_stat.pos_start_avg),
                str(career_stat.pos_finish_avg),
                str(career_stat.incidents_avg),
                str(career_stat.top_5_pcnt) + '%',
                str(career_stat.win_pcnt) + '%'
            ]
        )

    header_html_string = build_html_header_string(f'Career Stats for user: {iracing_id}')
    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    css = wrap_in_style_tag(iracing_table_css + header_css)

    return css + header_html_string + "\n" + html_string


def get_last_series_html_string(last_series, iracing_id):
    table = PrettyTable()
    table.field_names = ['Series', 'Position', 'Division', 'Weeks', 'Starts',
                         'Top 5s', 'Laps', 'Laps Led', 'Incidents', 'Champ Pts', 'Club Pts']

    for series in last_series:
        table.add_row([
            series.series_name_short,
            series.series_rank,
            series.division,
            series.weeks,
            series.starts,
            series.top_5s,
            series.laps,
            series.laps_led,
            series.incidents,
            series.points_champ,
            series.points_club
        ])

    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    header_string = build_html_header_string(f'Recent Series for user: {iracing_id}')
    css = wrap_in_style_tag(iracing_table_css + header_css)

    return css + header_string + "\n" + html_string


async def saved_users_irating_charts(guild_id, category):
    guild_dict = get_guild_dict(guild_id)
    category_string = Category(category).name

    iratings = []
    for user_id in guild_dict:
        if f'{category_string}_irating' in guild_dict[user_id]:
            iratings_list = guild_dict[user_id][f'{category_string}_irating']
            iratings_list_datetimes = []
            for irating_tuple in iratings_list:
                iratings_list_datetimes.append([
                    datetime.strptime(irating_tuple[0], datetime_format),
                    irating_tuple[1]
                ])

            iratings.append({
                user_id: iratings_list_datetimes
            })

    return iratings


def recent_races_table_string(recent_races, iracing_id, all_series):
    table = PrettyTable()
    table.field_names = ['Finish', 'Start', 'Incidents', 'Avg iRating', 'Race Date', 'Series', 'Track Name']

    for recent_race in recent_races:
        table.add_row(
            [
                'P' + str(recent_race.pos_finish),
                'P' + str(recent_race.pos_start),
                str(recent_race.incidents),
                str(recent_race.strength_of_field),
                recent_race.date,
                get_series_name(all_series, recent_race.series_id),
                recent_race.track
            ]
        )
    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    header_string = build_html_header_string(f'Recent Races for user: {iracing_id}')
    css = wrap_in_style_tag(iracing_table_css + header_css)

    return css + header_string + "\n" + html_string


def build_race_week_string(race_week, series, title, log):
    table = PrettyTable()
    table.field_names = ['ID', 'Series', 'Track']

    for serie in series:
        try:
            track = serie.tracks[race_week]
            track_name = track.name
            track_config = track.config

            if track_config:
                track_name += f' - {track_config}'
            table.add_row(
                [
                    serie.series_id,
                    serie.series_name_short,
                    track_name
                ]
            )
        except:
            log.info(f'failed to print series: {serie}')
            continue

    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    header_string = build_html_header_string(title)
    css = wrap_in_style_tag(iracing_table_css + header_css)

    return css + header_string + "\n" + html_string


def build_series_html_string(series, title):
    table = PrettyTable()
    table.field_names = ['ID', 'Series']

    for serie in series:
        try:
            table.add_row(
                [
                    serie.series_id,
                    serie.series_name_short
                ]
            )
        except:
            continue

    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    header_string = build_html_header_string(title)
    css = wrap_in_style_tag(iracing_table_css + header_css)

    return css + header_string + "\n" + html_string