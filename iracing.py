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

dotenv.load_dotenv()

logdna_key = os.getenv("LOGDNA_INGESTION_KEY")
log = logging.getLogger('logdna')
log.setLevel(logging.DEBUG)
handler = LogDNAHandler(logdna_key, {'hostname': os.getenv("LOG_LOCATION")})
log.addHandler(handler)


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


def print_yearly_stats(yearly_stats, iracing_id):
    string = 'Yearly Data for user: ' + str(iracing_id) + '\n\n'
    string += 'Year'.ljust(6) + \
              'Category'.ljust(11) + \
              'Starts'.ljust(8) + \
              'Top 5s'.ljust(8) + \
              'Wins'.ljust(8) + \
              'Avg Start'.ljust(12) + \
              'Avg Finish'.ljust(12) + \
              'Avg Incidents'.ljust(15) + \
              'Top 5 %'.ljust(9) + \
              'Win %'.ljust(7) + '\n'
    string += '--------------------------------------------------------------------' \
              '---------------------------\n'

    for yearly_stat in yearly_stats[:16]:
        string += str(yearly_stat.year).ljust(6) + \
                  yearly_stat.category.ljust(11) + \
                  str(yearly_stat.starts).ljust(8) + \
                  str(yearly_stat.top_5s).ljust(8) + \
                  str(yearly_stat.wins).ljust(8) + \
                  str(yearly_stat.pos_start_avg).ljust(12) + \
                  str(yearly_stat.pos_finish_avg).ljust(12) + \
                  str(yearly_stat.incidents_avg).ljust(15) + \
                  str(yearly_stat.top_5_pcnt).ljust(9) + \
                  str(yearly_stat.win_pcnt).ljust(7) + '\n'

    return add_backticks(string)


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


def print_leaderboard(user_data_list, guild, category, yearly=False):
    type_string = 'Yearly' if yearly else 'Career'
    minutes_since_update = minutes_since_last_update(guild.id)
    time_since_update_string = f' - Last updated {minutes_since_update} minute(s) ago' if minutes_since_update else ''

    string = 'iRacing ' + lowercase_to_readable_categories(category) + ' ' + \
             type_string + ' Leaderboard' + time_since_update_string + '\n\n'
    string += 'Racer'.ljust(16) + \
              'Starts'.ljust(8) + \
              'iRating'.ljust(9) + \
              'License'.ljust(9) + \
              'Wins'.ljust(8) + \
              'Top 5s'.ljust(8) + \
              'Laps Led'.ljust(10) + \
              'Win %'.ljust(9) + \
              'Top 5 %'.ljust(9) + \
              'Laps Led %'.ljust(12) + \
              'Avg Incidents'.ljust(15) + '\n'
    string += '----------------------------------------------------------------------------------------------------' \
              '-----------\n'

    for item in user_data_list:
        try:
            member = discord.utils.find(lambda m: m.id == int(item[0]), guild.members)
            if yearly:
                stats_list = get_current_year_stats(item[-1]['yearly_stats'])
            else:
                stats_list = item[-1]['career_stats']

            irating = 0
            if category == 'road':
                irating = item[-1]['road_irating']
            elif category == 'oval':
                irating = item[-1]['oval_irating']
            elif category == 'dirtroad':
                irating = item[-1]['dirt_road_irating']
            elif category == 'dirtoval':
                irating = item[-1]['dirt_oval_irating']

            license_class = 'N/A'
            if category == 'road':
                license_class = item[-1]['road_license_class']
            elif category == 'oval':
                license_class = item[-1]['oval_license_class']
            elif category == 'dirtroad':
                license_class = item[-1]['dirt_road_license_class']
            elif category == 'dirtoval':
                license_class = item[-1]['dirt_oval_license_class']

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
                string += member.name.ljust(16) + \
                          str(career_stats['starts']).ljust(8) + \
                          str(irating).ljust(9) + \
                          str(license_class).ljust(9) + \
                          str(career_stats['wins']).ljust(8) + \
                          str(career_stats['top_5s']).ljust(8) + \
                          str(career_stats['laps_led']).ljust(10) + \
                          str(career_stats['win_pcnt']).ljust(9) + \
                          str(career_stats['top_5_pcnt']).ljust(9) + \
                          str(career_stats['laps_led_pcnt']).ljust(12) + \
                          str(career_stats['incidents_avg']).ljust(15) + '\n'
        except Exception as e:
            log.error(e)
            log.error(f'Error printing leaderboard data for user: {item}')
            continue

    return add_backticks(string)


def get_current_year_stats(yearly_stats_list):
    """This takes the massive list of a user's yearly stats dicts
    and returns just the yearly stats from the current year"""
    current_year = str(datetime.now().year)
    return filter(lambda x: x['year'] == current_year, yearly_stats_list)


def print_career_stats(career_stats, iracing_id):
    string = 'Career Data for user: ' + str(iracing_id) + '\n\n'
    string += 'Category'.ljust(11) + \
              'Starts'.ljust(8) + \
              'Top 5s'.ljust(8) + \
              'Wins'.ljust(8) + \
              'Avg Start'.ljust(12) + \
              'Avg Finish'.ljust(12) + \
              'Avg Incidents'.ljust(15) + \
              'Top 5 %'.ljust(9) + \
              'Win %'.ljust(8) + '\n'
    string += '--------------------------------------------------------------------' \
              '---------------------\n'

    for career_stat in career_stats:
        string += career_stat.category.ljust(11) + \
                  str(career_stat.starts).ljust(8) + \
                  str(career_stat.top_5s).ljust(8) + \
                  str(career_stat.wins).ljust(8) + \
                  str(career_stat.pos_start_avg).ljust(12) + \
                  str(career_stat.pos_finish_avg).ljust(12) + \
                  str(career_stat.incidents_avg).ljust(15) + \
                  str(career_stat.top_5_pcnt).ljust(9) + \
                  str(career_stat.win_pcnt).ljust(8) + '\n'

    return add_backticks(string)


def get_relevant_leaderboard_data(guild_dict, category):
    if category == 'road':
        valid_guild_dict = dict(filter(
            lambda x: 'road_irating' in x[1],
            guild_dict.items()
        ))
        return sorted(valid_guild_dict.items(), key=lambda x: int(x[1]['road_irating']), reverse=True)
    elif category == 'oval':
        valid_guild_dict = dict(filter(
            lambda x: 'oval_irating' in x[1],
            guild_dict.items()
        ))
        return sorted(valid_guild_dict.items(), key=lambda x: int(x[1]['oval_irating']), reverse=True)
    elif category == 'dirtroad':
        valid_guild_dict = dict(filter(
            lambda x: 'dirt_road_irating' in x[1],
            guild_dict.items()
        ))
        return sorted(valid_guild_dict.items(), key=lambda x: int(x[1]['dirt_road_irating']), reverse=True)
    elif category == 'dirtoval':
        valid_guild_dict = dict(filter(
            lambda x: 'dirt_oval_irating' in x[1],
            guild_dict.items()
        ))
        return sorted(valid_guild_dict.items(), key=lambda x: int(x[1]['dirt_oval_irating']), reverse=True)

    return []


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
        log.info('=============== Auto update took ' + str((finish_time - start_time).total_seconds()) + ' seconds =================')

        self.all_series = await self.pyracing.current_seasons(series_id=True)
        log.info('Successfully got all current season data')

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
        log.info('=============== Manual update took ' + str((finish_time - start_time).total_seconds()) + ' seconds ===============')
        await ctx.send("Successfully updated this server")

    @commands.command()
    async def recentraces(self, ctx, *, iracing_id=None):
        """Shows the recent race data for the given iracing id. If no iracing id is provided it will attempt
        to use the stored iracing id for the user who called the command."""

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
            await ctx.send(self.print_recent_races(races_stats_list, iracing_id))
        else:
            await ctx.send('Recent races not found for user: ' + iracing_id)

    @commands.command()
    async def yearlystats(self, ctx, *, iracing_id=None):
        """Shows the yearly stats for the given iracing id. If no iracing id is provided it will attempt
        to use the stored iracing id for the user who called the command."""

        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        if not iracing_id:
            iracing_id = get_user_iracing_id(user_id, guild_id)
            if not iracing_id:
                await ctx.send('Please send an iRacing ID after the command or link your own with `!saveid <iRacing '
                               'ID>`')
                return

        yearly_stats = await self.update_yearly_stats(user_id, guild_id, iracing_id)

        if yearly_stats:
            await ctx.send(print_yearly_stats(yearly_stats, iracing_id))
        else:
            await ctx.send('No yearly stats found for user: ' + str(iracing_id))

    @commands.command()
    async def careerstats(self, ctx, *, iracing_id=None):
        """Shows the career stats for the given iracing id. If no iracing id is provided it will attempt
        to use the stored iracing id for the user who called the command."""

        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        if not iracing_id:
            iracing_id = get_user_iracing_id(user_id, guild_id)
            if not iracing_id:
                await ctx.send('Please send an iRacing ID after the command or link your own with `!saveid <iRacing '
                               'ID>`')
                return

        career_stats = await self.update_career_stats(user_id, guild_id, iracing_id)

        if career_stats:
            await ctx.send(print_career_stats(career_stats, iracing_id))
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
        is_yearly = (type != 'career')

        if category not in ['road', 'oval', 'dirtroad', 'dirtoval']:
            await ctx.send('Please try again with one of these categories: `road`, `oval`, `dirtroad`, `dirtoval`')
            return

        guild_dict = get_guild_dict(ctx.guild.id)
        leaderboard_data = get_relevant_leaderboard_data(guild_dict, category)
        await ctx.send(print_leaderboard(leaderboard_data, ctx.guild, category, is_yearly))

    async def update_user_in_dict(self, user_id, guild_dict):
        """This updates a user inside the dict without saving to any files"""
        iracing_id = guild_dict[user_id]['iracing_id']
        career_stats_list = await self.pyracing.career_stats(iracing_id)
        if career_stats_list:
            guild_dict[user_id]['career_stats'] = list(map(lambda x: x.__dict__, career_stats_list))

        yearly_stats_list = await self.pyracing.yearly_stats(iracing_id)
        if yearly_stats_list:
            guild_dict[user_id]['yearly_stats'] = list(map(lambda x: x.__dict__, yearly_stats_list))

        guild_dict[user_id]['oval_irating'] = await self.get_irating(iracing_id, Category.oval.value)
        guild_dict[user_id]['road_irating'] = await self.get_irating(iracing_id, Category.road.value)
        guild_dict[user_id]['dirt_road_irating'] = await self.get_irating(iracing_id, Category.dirt_road.value)
        guild_dict[user_id]['dirt_oval_irating'] = await self.get_irating(iracing_id, Category.dirt_oval.value)

        guild_dict[user_id]['oval_license_class'] = await self.get_license_class(iracing_id, Category.oval.value)
        guild_dict[user_id]['road_license_class'] = await self.get_license_class(iracing_id, Category.road.value)
        guild_dict[user_id]['dirt_oval_license_class'] = await self.get_license_class(iracing_id, Category.dirt_oval.value)
        guild_dict[user_id]['dirt_road_license_class'] = await self.get_license_class(iracing_id, Category.dirt_road.value)

        return guild_dict

    async def update_last_races(self, user_id, guild_id, iracing_id):
        races_stats_list = await self.pyracing.last_races_stats(iracing_id)
        if races_stats_list:
            log.info('found a races stats list for user: ' + str(iracing_id))
            update_user(user_id, guild_id, None, None, copy.deepcopy(races_stats_list))
            return races_stats_list

    async def update_yearly_stats(self, user_id, guild_id, iracing_id):
        yearly_stats_list = await self.pyracing.yearly_stats(iracing_id)
        if yearly_stats_list:
            update_user(user_id, guild_id, None, copy.deepcopy(yearly_stats_list), None)
            return yearly_stats_list

    async def update_career_stats(self, user_id, guild_id, iracing_id):
        career_stats_list = await self.pyracing.career_stats(iracing_id)
        if career_stats_list:
            update_user(user_id, guild_id, copy.deepcopy(career_stats_list), None, None)
            return career_stats_list

    async def get_irating(self, user_id, category):
        chart_data = await self.pyracing.irating(category, user_id)
        if not chart_data.current():
            return 0
        return str(chart_data.current().value)

    async def get_license_class(self, user_id, category):
        chart_data = await self.pyracing.license_class(category, user_id)
        if not chart_data.current():
            return 'N/A'
        return str(chart_data.current().class_letter()) + ' ' + str(chart_data.current().license_level)

    def get_series_name(self, series_id):
        for series in self.all_series:
            if str(series.series_id) == str(series_id):
                # We want to truncate the series name to 35 because some of them are massive
                return series.series_name_short[:33] + '..' if len(series.series_name_short) > 35 else series.series_name_short

        return "Unknown Series"

    def print_recent_races(self, recent_races, iracing_id):
        string = 'Recent Races Data for user: ' + str(iracing_id) + '\n\n'
        string += 'Finish'.ljust(8) + \
                  'Start'.ljust(8) + \
                  'Incidents'.ljust(11) + \
                  'Avg iRating'.ljust(13) + \
                  'Race Date'.ljust(15) + \
                  'Series'.ljust(38) + \
                  'Track Name'.ljust(30) + '\n'
        string += '------------------------------------------------------------------------------------' \
                  '-----------------------\n'

        for recent_race in recent_races:
            string += ('P' + str(recent_race.pos_finish)).ljust(8) + \
                      ('P' + str(recent_race.pos_start)).ljust(8) + \
                      str(recent_race.incidents).ljust(11) + \
                      str(recent_race.strength_of_field).ljust(13) + \
                      recent_race.date.ljust(15) + \
                      self.get_series_name(recent_race.series_id).ljust(38) + \
                      recent_race.track.ljust(30) + '\n'

        return add_backticks(string)
