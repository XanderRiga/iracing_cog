from redbot.core import commands
import dotenv
from pyracing import client as pyracing
from pyracing.constants import Category
from .storage import *
import copy
import discord
from discord.ext import tasks
from .storage import folder
from datetime import datetime
import logging
from logdna import LogDNAHandler
from prettytable import PrettyTable, ALL
import imgkit
from .helpers import *
from .errors.name_not_found import NameNotFound
from bokeh.plotting import figure, output_file, save
from bokeh.io import export_png
from bokeh.palettes import Category20
from bokeh.models import Legend
import itertools
from selenium import webdriver
import asyncio

options = webdriver.chrome.options.Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--headless")
options.add_argument("--hide-scrollbars")

dotenv.load_dotenv()

logdna_key = os.getenv("LOGDNA_INGESTION_KEY")
log = logging.getLogger('logdna')
log.setLevel(logging.DEBUG)
handler = LogDNAHandler(logdna_key, {'hostname': os.getenv("LOG_LOCATION")})
log.addHandler(handler)


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


def minutes_since_last_update(guild_id):
    try:
        last_update = get_last_update_datetime(guild_id)
        if not last_update:
            return None
        return round((datetime.now() - last_update).seconds / 60, 1)
    except Exception as e:
        log.warning('datetime parsing exploded')
        log.warning(e)
        return None


def get_leaderboard_html_string(user_data_list, guild, category, yearly=False):
    type_string = 'Yearly' if yearly else 'Career'
    minutes_since_update = minutes_since_last_update(guild.id)
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
                        member.name,
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


class Iracing(commands.Cog):
    """A cog that can give iRacing data about users"""

    def __init__(self):
        super().__init__()
        self.pyracing = pyracing.Client(
            os.getenv("IRACING_USERNAME"),
            os.getenv("IRACING_PASSWORD"),
            log
        )
        self.all_series = []
        self.update_all_servers.start()

    @tasks.loop(hours=1, reconnect=False)
    async def update_all_servers(self):
        """Update all users career stats and iratings for building a current leaderboard"""
        start_time = datetime.now()
        dt_string = start_time.strftime("%d/%m/%Y %H:%M:%S")
        log.info('=============== Updating all user stats: ' + dt_string + ' ======================')

        self.all_series = await self.pyracing.current_seasons(series_id=True)
        log.info('Successfully got all current season data')

        guilds = []
        for file in os.scandir(folder):
            if file.path.endswith('.json'):
                guilds.append(os.path.basename(file.path)[:-5])

        for guild_id in guilds:
            guild_dict = get_guild_dict(guild_id)
            for user_id in guild_dict:
                if 'iracing_id' in guild_dict[user_id]:
                    guild_dict = await self.update_user_in_dict(user_id, guild_dict)

            set_guild_data(guild_id, guild_dict)

        log.info('=============== Finished update that started at: ' + dt_string + ' ======================')
        finish_time = datetime.now()
        log.info('=============== Auto update took ' + str(
            (finish_time - start_time).total_seconds()) + ' seconds =================')

    @commands.command()
    async def update(self, ctx):
        """Update all users career and yearly stats and iratings for building a current leaderboard.
        This is run every hour anyways, so it isn't necessary most of the time to run manually"""
        start_time = datetime.now()
        dt_string = start_time.strftime("%d/%m/%Y %H:%M:%S")
        log.info('=============== Manual update started at: ' + dt_string + ' ======================')

        await ctx.send("Updating all users in this server, this may take a few minutes")
        guild_id = str(ctx.guild.id)
        guild_dict = get_guild_dict(guild_id)
        for user_id in guild_dict:
            if 'iracing_id' in guild_dict[user_id]:
                guild_dict = await self.update_user_in_dict(user_id, guild_dict)

        set_guild_data(guild_id, guild_dict)
        log.info('=============== Manual update finished that started at: ' + dt_string + ' ======================')
        finish_time = datetime.now()
        log.info('=============== Manual update took ' + str(
            (finish_time - start_time).total_seconds()) + ' seconds ===============')
        await ctx.send("Successfully updated this server")

    @commands.command()
    async def recentraces(self, ctx, *, iracing_id=None):
        """Shows the recent race data for the given iracing id. If no iracing id is provided it will attempt
        to use the stored iracing id for the user who called the command."""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            if not iracing_id:
                iracing_id = get_user_iracing_id(user_id, guild_id)
                if not iracing_id:
                    await ctx.send('Please send an iRacing ID with the command or link your own with `!saveid <iRacing '
                                   'ID>`')
                    return

            races_stats_list = await self.update_last_races(user_id, guild_id, iracing_id)

            if races_stats_list:
                table_html_string = self.recent_races_table_string(races_stats_list, iracing_id)
                imgkit.from_string(table_html_string, f'{guild_id}_{iracing_id}_recent_races.jpg')
                await ctx.send(file=discord.File(f'{guild_id}_{iracing_id}_recent_races.jpg'))
            else:
                await ctx.send('Recent races not found for user: ' + iracing_id)

    @commands.command()
    async def lastseries(self, ctx, *, iracing_id=None):
        """Shows the recent series data for the given iracing id. If no iracing id is provided it will attempt
        to use the stored iracing id for the user who called the command."""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            if not iracing_id:
                iracing_id = get_user_iracing_id(user_id, guild_id)
                if not iracing_id:
                    await ctx.send('Please send an iRacing ID with the command or link your own with `!saveid <iRacing '
                                   'ID>`')
                    return

            last_series = await self.pyracing.last_series(iracing_id)

            if last_series:
                table_html_string = get_last_series_html_string(last_series, iracing_id)
                imgkit.from_string(table_html_string, f'{guild_id}_{iracing_id}_last_series.jpg')
                await ctx.send(file=discord.File(f'{guild_id}_{iracing_id}_last_series.jpg'))
            else:
                await ctx.send('Recent races not found for user: ' + iracing_id)

    @commands.command()
    async def yearlystats(self, ctx, *, iracing_id=None):
        """Shows the yearly stats for the given iracing id. If no iracing id is provided it will attempt
        to use the stored iracing id for the user who called the command."""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            if not iracing_id:
                iracing_id = get_user_iracing_id(user_id, guild_id)
                if not iracing_id:
                    await ctx.send('Please send an iRacing ID after the command or link your own with `!saveid <iRacing '
                                   'ID>`')
                    return

            guild_dict = get_guild_dict(guild_id)
            yearly_stats = await self.update_yearly_stats(user_id, guild_dict, iracing_id)

            if yearly_stats:
                yearly_stats_html = get_yearly_stats_html(yearly_stats, iracing_id)
                imgkit.from_string(yearly_stats_html, f'{iracing_id}_yearly_stats.jpg')
                await ctx.send(file=discord.File(f'{iracing_id}_yearly_stats.jpg'))
            else:
                await ctx.send('No yearly stats found for user: ' + str(iracing_id))

    @commands.command()
    async def careerstats(self, ctx, *, iracing_id=None):
        """Shows the career stats for the given iracing id. If no iracing id is provided it will attempt
        to use the stored iracing id for the user who called the command."""
        async with ctx.typing():
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            if not iracing_id:
                iracing_id = get_user_iracing_id(user_id, guild_id)
                if not iracing_id:
                    await ctx.send('Please send an iRacing ID after the command or link your own with `!saveid <iRacing'
                                   ' ID>`')
                    return

            guild_dict = get_guild_dict(guild_id)
            career_stats = await self.update_career_stats(user_id, guild_dict, iracing_id)

            if career_stats:
                career_stats_html = get_career_stats_html(career_stats, iracing_id)
                imgkit.from_string(career_stats_html, f'{iracing_id}_career_stats.jpg')
                await ctx.send(file=discord.File(f'{iracing_id}_career_stats.jpg'))
            else:
                await ctx.send('No career stats found for user: ' + str(iracing_id))

    @commands.command()
    async def saveid(self, ctx, *, iracing_id):
        """Save your iRacing ID to be placed on the leaderboard.
        Your ID can be found by the top right of your account page under "Customer ID"."""

        if not iracing_id.isdigit():
            await ctx.send('Oops, this ID does not seem to be valid. '
                           + 'Make sure you only write the numbers and not any symbols with the ID.'
                           + 'Your ID can be found by the top right of your account page under "Customer ID".')
            return

        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        save_iracing_id(user_id, guild_id, iracing_id)
        await ctx.send('iRacing ID successfully saved. Use `!update` to see this user on the leaderboard.')

    @commands.command()
    async def leaderboard(self, ctx, category='road', type='career'):
        """Displays a leaderboard of the users who have used `!saveid`.
        If the data is not up to date, try `!update` first.
        The categories are `road`, `oval`, `dirtroad`, and `dirtoval` and
        the types are `career` and `yearly`. Default is `road` `career`"""
        async with ctx.typing():
            if type not in ['career', 'yearly']:
                await ctx.send('Please try again with one of these types: `career`, `yearly`')
                return

            if category not in ['road', 'oval', 'dirtroad', 'dirtoval']:
                await ctx.send('Please try again with one of these categories: `road`, `oval`, `dirtroad`, `dirtoval`')
                return

            is_yearly = (type != 'career')

            guild_dict = get_guild_dict(ctx.guild.id)
            leaderboard_data = get_relevant_leaderboard_data(guild_dict, category)
            table_html_string = get_leaderboard_html_string(leaderboard_data, ctx.guild, category, is_yearly)
            imgkit.from_string(table_html_string, f'{ctx.guild.id}_leaderboard.jpg')
            await ctx.send(file=discord.File(f'{ctx.guild.id}_leaderboard.jpg'))

    @commands.command()
    async def iratings(self, ctx, category='road'):
        async with ctx.typing():
            if category not in ['road', 'oval', 'dirtroad', 'dirtoval']:
                ctx.send('The category should be one of `road`, `oval`, `dirtroad`, `dirtoval`')
                return

            category_id = category_id_from_string(category)

            today = datetime.now()
            date_6mo_ago = datetime(today.year, today.month - 6, today.day)

            p = figure(
                title=f'{lowercase_to_readable_categories(category)} iRatings',
                x_axis_type='datetime',
                x_range=(date_6mo_ago, datetime.now())
            )
            p.toolbar.logo = None
            p.toolbar_location = None
            legend = Legend(location=(0, -10))
            p.add_layout(legend, 'right')
            output_file('output_iratings.html')

            colors = itertools.cycle(Category20[20])

            irating_dicts = await saved_users_irating_charts(ctx.guild.id, category_id)
            for irating_dict in irating_dicts:
                for user_id, iratings_list in irating_dict.items():
                    member = ctx.guild.get_member(int(user_id))
                    datetimes = []
                    iratings = []
                    for irating in iratings_list:
                        datetimes.append(irating[0])
                        iratings.append(irating[1])

                    p.line(
                        datetimes,
                        iratings,
                        legend_label=member.display_name,
                        line_width=2,
                        color=next(colors)
                    )

            export_png(p, filename=f'irating_graph_{ctx.guild.id}.png', webdriver=webdriver.Chrome(options=options))
            await ctx.send(file=discord.File(f'irating_graph_{ctx.guild.id}.png'))

    async def update_user_in_dict(self, user_id, guild_dict):
        """This updates a user inside the dict without saving to any files"""
        iracing_id = guild_dict[user_id]['iracing_id']

        # We want to break this into a few sections because if the bot
        # receives a request from a user we don't want this to block that from happening
        # Yea, this is a hacky workaround, but I need a way to prioritize the inputs from users.
        # When I store all the user data so I don't need to make requests on user input this can all be one gather.
        await asyncio.gather(
            self.update_driver_name(user_id, guild_dict, iracing_id),
            self.update_career_stats(user_id, guild_dict, iracing_id),
            self.update_yearly_stats(user_id, guild_dict, iracing_id),
            return_exceptions=True
        )
        await asyncio.gather(
            self.update_iratings(user_id, guild_dict, iracing_id, Category.oval),
            self.update_iratings(user_id, guild_dict, iracing_id, Category.road),
            self.update_iratings(user_id, guild_dict, iracing_id, Category.dirt_road),
            self.update_iratings(user_id, guild_dict, iracing_id, Category.dirt_oval),
            return_exceptions=True
        )
        await asyncio.gather(
            self.update_license_class(user_id, guild_dict, iracing_id, Category.oval),
            self.update_license_class(user_id, guild_dict, iracing_id, Category.road),
            self.update_license_class(user_id, guild_dict, iracing_id, Category.dirt_road),
            self.update_license_class(user_id, guild_dict, iracing_id, Category.dirt_oval),
            return_exceptions=True
        )

        return guild_dict

    async def update_driver_name(self, user_id, guild_dict, cust_id):
        try:
            response = await self.pyracing.driver_status(cust_id=cust_id)
            name = parse_encoded_string(response.name)
            guild_dict[user_id]['name'] = name
            return name
        except:
            log.warning(f'Name not found for {cust_id}')
            raise NameNotFound

    async def update_career_stats(self, user_id, guild_dict, iracing_id):
        career_stats_list = await self.pyracing.career_stats(iracing_id)
        if career_stats_list:
            guild_dict[user_id]['career_stats'] = list(map(lambda x: x.__dict__, career_stats_list))
            return career_stats_list
        else:
            return []

    async def update_yearly_stats(self, user_id, guild_dict, iracing_id):
        yearly_stats_list = await self.pyracing.yearly_stats(iracing_id)
        if yearly_stats_list:
            guild_dict[user_id]['yearly_stats'] = list(map(lambda x: x.__dict__, yearly_stats_list))
            return yearly_stats_list
        else:
            return []

    async def update_iratings(self, user_id, guild_dict, iracing_id, category):
        chart_data = await self.pyracing.irating(iracing_id, category.value)
        if not chart_data.current():
            return []

        json_iratings = []
        for irating in chart_data.list:
            json_iratings.append([irating.datetime.strftime(datetime_format), irating.value])

        guild_dict[user_id][f'{category.name}_irating'] = json_iratings

        return json_iratings

    async def update_license_class(self, user_id, guild_dict, iracing_id, category):
        chart_data = await self.pyracing.license_class(iracing_id, category.value)
        if not chart_data.current():
            return 'N/A'

        license_class = str(chart_data.current().class_letter()) + ' ' + str(chart_data.current().license_level)
        guild_dict[user_id][f'{category.name}_license_class'] = license_class
        return license_class

    async def update_last_races(self, user_id, guild_id, iracing_id):
        races_stats_list = await self.pyracing.last_races_stats(iracing_id)
        if races_stats_list:
            log.info('found a races stats list for user: ' + str(iracing_id))
            update_user(user_id, guild_id, None, None, copy.deepcopy(races_stats_list))
            return races_stats_list

    def get_series_name(self, series_id):
        for series in self.all_series:
            if str(series.series_id) == str(series_id):
                # We want to truncate the series name to 35 because some of them are massive
                return series.series_name_short[:33] + '..' if len(
                    series.series_name_short) > 35 else series.series_name_short

        return "Unknown Series"

    def recent_races_table_string(self, recent_races, iracing_id):
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
                    self.get_series_name(recent_race.series_id),
                    recent_race.track
                ]
            )
        html_string = table.get_html_string(attributes={"id": "iracing_table"})
        header_string = build_html_header_string(f'Recent Races for user: {iracing_id}')
        css = wrap_in_style_tag(iracing_table_css + header_css)

        return css + header_string + "\n" + html_string
