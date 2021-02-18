from .helpers import *
from prettytable import PrettyTable
import discord
from .db_helpers import init_tortoise
from .models import Series


def get_yearly_stats_html_db(yearly_stats, iracing_id):
    table = PrettyTable()
    table.field_names = [
        'Year', 'Category', 'Starts', 'Top 5s', 'Wins', 'Avg Start', 'Avg Finish', 'Avg Incidents', 'Top 5 %', 'Win %'
    ]
    for yearly_stat in yearly_stats:
        table.add_row(
            [
                str(yearly_stat.year),
                yearly_stat.category.friendly_name(),
                str(yearly_stat.total_starts),
                str(yearly_stat.total_top_fives),
                str(yearly_stat.total_wins),
                str(yearly_stat.avg_start_pos),
                str(yearly_stat.avg_finish_pos),
                str(yearly_stat.avg_incidents),
                str(yearly_stat.top_five_percentage) + '%',
                str(yearly_stat.win_percentage) + '%'
            ]
        )

    header_html_string = build_html_header_string(f'Yearly Stats for user: {iracing_id}')
    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    css = wrap_in_style_tag(iracing_table_css + header_css)

    return css + header_html_string + "\n" + html_string


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


def get_career_stats_html_db(career_stats, iracing_id):
    table = PrettyTable()
    table.field_names = [
        'Category', 'Starts', 'Top 5s', 'Wins', 'Avg Start', 'Avg Finish', 'Avg Incidents', 'Top 5 %', 'Win %'
    ]
    for career_stat in career_stats:
        table.add_row(
            [
                career_stat.category.friendly_name(),
                str(career_stat.total_starts),
                str(career_stat.total_top_fives),
                str(career_stat.total_wins),
                str(career_stat.avg_start_pos),
                str(career_stat.avg_finish_pos),
                str(career_stat.avg_incidents),
                str(career_stat.top_five_percentage) + '%',
                str(career_stat.win_percentage) + '%'
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


def recent_races_table_string(recent_races, iracing_id, all_series):
    table = PrettyTable()
    table.field_names = ['Finish', 'Start', 'Incidents', 'SoF', 'Race Date', 'Series', 'Track Name']

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


async def recent_races_table_db_string(recent_races, iracing_id):
    table = PrettyTable()
    table.field_names = ['Finish', 'Start', 'Incidents', 'SoF', 'Race Date', 'Series', 'Track Name']

    for recent_race in recent_races:
        try:

            series = await Series.get(iracing_id=recent_race.series_id)
            series_name = series.name
        except:
            series_name = 'Unknown Series'
        table.add_row(
            [
                'P' + str(recent_race.pos_finish),
                'P' + str(recent_race.pos_start),
                str(recent_race.incidents),
                str(recent_race.strength_of_field),
                recent_race.date,
                series_name,
                recent_race.track
            ]
        )
    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    header_string = build_html_header_string(f'Recent Races for user: {iracing_id}')
    css = wrap_in_style_tag(iracing_table_css + header_css)

    return css + charset() + header_string + "\n" + html_string


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


async def build_race_week_string_db(series, title, log, offset):
    table = PrettyTable()
    table.field_names = ['ID', 'Series', 'Track']
    added_rows = 0


    for serie in series:

        season = await serie.current_season()
        combo = await season.offset_combo(offset)
        if not combo:
            continue
        track = await combo.track

        try:
            track_name = track.name

            if combo.track_layout:
                track_name += f' - {combo.track_layout}'
            table.add_row(
                [
                    serie.iracing_id,
                    serie.name,
                    track_name
                ]
            )
            added_rows += 1
        except:
            log.info(f'failed to print series: {serie}')
            continue

    # If we couldn't find any combos to print, lets give back an empty response
    if added_rows == 0:
        return ''
    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    header_string = build_html_header_string(title)
    css = wrap_in_style_tag(iracing_table_css + header_css)

    return css + charset() + header_string + "\n" + html_string


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


def build_series_model_html_string(series, title):
    table = PrettyTable()
    table.field_names = ['ID', 'Series']

    for serie in series:
        try:
            table.add_row(
                [
                    serie.iracing_id,
                    serie.name
                ]
            )
        except:
            continue

    html_string = table.get_html_string(attributes={"id": "iracing_table"})
    header_string = build_html_header_string(title)
    css = wrap_in_style_tag(iracing_table_css + header_css)

    return css + header_string + "\n" + html_string
