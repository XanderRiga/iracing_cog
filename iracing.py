import logging
import dotenv
from pyracing import client as pyracing
from discord.ext import commands, tasks
from logdna import LogDNAHandler
from .html_builder import *
from .commands.update_user import UpdateUser
from .commands.update import Update
from .commands.recent_races import RecentRaces
# from .commands.last_series import LastSeries
from .commands.career_stats_db import CareerStatsDb
from .commands.yearly_stats_db import YearlyStatsDb
from .commands.save_id import SaveId
from .commands.save_name import SaveName
from .commands.iratings_db import IratingsDb
from .commands.all_series_db import AllSeriesDb
from .commands.set_fav_series import SetFavSeries
from .commands.remove_fav_series import RemoveFavSeries
from .commands.current_series_db import CurrentSeriesDb
from .commands.leaderboard_db import LeaderboardDb
from .commands.save_league import SaveLeague
from .commands.remove_league import RemoveLeague
from .commands.league_standings import LeagueStandings
from .db_helpers import *

dotenv.load_dotenv()

logdna_key = os.getenv("LOGDNA_INGESTION_KEY")
log = logging.getLogger('logdna')
log.setLevel(logging.DEBUG)
handler = LogDNAHandler(logdna_key, {'hostname': os.getenv("LOG_LOCATION")})
log.addHandler(handler)


class Iracing(commands.Cog):
    """A cog that can give iRacing data about users"""

    def __init__(self, bot):
        self.bot = bot
        self.pyracing = pyracing.Client(
            os.getenv("IRACING_USERNAME"),
            os.getenv("IRACING_PASSWORD")
        )
        self.update_user = UpdateUser(self.pyracing, log)
        self.updater = Update(self.pyracing, log, self.update_user)
        self.recent_races = RecentRaces(self.pyracing, log)
        # self.last_series = LastSeries(self.pyracing, log)
        self.yearly_stats_db = YearlyStatsDb(self.pyracing, log)
        self.career_stats_db = CareerStatsDb(self.pyracing, log)
        self.save_id = SaveId(log)
        self.save_name = SaveName(self.pyracing, log)
        self.iratings_db = IratingsDb(log)
        self.all_series_db = AllSeriesDb(log)
        self.current_series_db = CurrentSeriesDb(log)
        self.set_fav_series = SetFavSeries(log)
        self.remove_fav_series = RemoveFavSeries(log)
        self.leaderboard_db = LeaderboardDb(log)
        self.save_league = SaveLeague(self.pyracing, log)
        self.remove_league = RemoveLeague(log)
        self.league_standings = LeagueStandings(self.pyracing, log)
        # self.migrate_fav_series.start()
        self.update_all_servers.start()
        self.update_series.start()

    @tasks.loop(hours=3)
    async def update_all_servers(self):
        """Update all users career stats and iratings for building a current leaderboard"""
        await self.updater.update_all_servers()

    @tasks.loop(hours=12)
    async def update_series(self):
        """Update all series data, this does nothing 99% of the time,
        but when a new season start it gets the new stuff"""
        log.info('Updating all series')
        await self.updater.update_series()
        log.info('Done updating all series')

    @commands.command(name='update')
    async def update(self, ctx):
        """Update the career, yearly stats, and iratings for the user who called the command in the given server"""
        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return
        await ctx.send(f'Updating user: {ctx.author.name}, this may take a minute')
        log.info(f'Updating user: {ctx.author.name}')
        await self.updater.update_member(ctx)

    @commands.command(name='updateserver')
    async def updateserver(self, ctx):
        """Update all users career and yearly stats and iratings for building a current leaderboard.
        This is run every hour anyways, so it isn't necessary most of the time to run manually"""
        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return

        await ctx.send(f'Updating server data. This may take a while')

        try:
            guild = await Guild.get(discord_id=str(ctx.guild.id))
            await self.updater.update_server_background(guild)
            await ctx.send(f'Server update complete!')
        except:
            await ctx.send('Make sure at least 1 user has set their ID with `!saveid` before calling this command')

    @commands.command(name='recentraces')
    async def recentraces(self, ctx, *, iracing_id=None):
        """Shows the recent race data for the given iracing id. If no iracing id is provided it will attempt
        to use the stored iracing id for the user who called the command."""
        await self.recent_races.call(ctx, iracing_id)

    # @commands.command(name='lastseries')
    # async def lastseries(self, ctx, *, iracing_id=None):
    #     """Shows the recent series data for the given iracing id. If no iracing id is provided it will attempt
    #     to use the stored iracing id for the user who called the command."""
    #     await self.last_series.call(ctx, iracing_id)

    @commands.command(name='yearlystats')
    async def yearlystats(self, ctx, *, iracing_id=None):
        """Shows the yearly stats for the given iracing id. If no iracing id is provided it will attempt
        to use the stored iracing id for the user who called the command."""
        await self.yearly_stats_db.call(ctx, iracing_id)

    @commands.command(name='careerstats')
    async def careerstats(self, ctx, *, iracing_id=None):
        """Shows the career stats for the given iracing id. If no iracing id is provided it will attempt
        to use the stored iracing id for the user who called the command."""
        await self.career_stats_db.call(ctx, iracing_id)

    @commands.command(name='saveid')
    async def saveid(self, ctx, *, iracing_id):
        """Save your iRacing ID to be placed on the leaderboard.
        Your ID can be found by the top right of your account page under "Customer ID"."""
        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return
        await self.save_id.call(ctx, iracing_id)

    @commands.command(name='savename')
    async def savename(self, ctx, *, iracing_name):
        """Save your iRacing name with this command.
        The name must be exactly as you see it on the site including the numbers if there are any"""
        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, savename, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return
        await self.save_name.call(ctx, iracing_name)

    @commands.command(name='saveleague')
    async def saveleague(self, ctx, *, league_id):
        """Save a league to this discord. The league ID can be found by navigating to the league home page on iRacing,
        the URL will have `league=ID` where ID is the league ID you can enter"""
        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return

        await self.save_league.call(ctx, league_id)

    @commands.command(name='removeleague')
    async def removeleague(self, ctx, *, league_id):
        """Remove a league saved to this discord. The league IDs currently
        can be found by running `!leaguestandings`"""
        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return

        await self.remove_league.call(ctx, league_id)

    @commands.command(name='leaguestandings')
    async def leaguestandings(self, ctx):
        """Get the standings for all saved league's active seasons.
        This only shows active seasons, so if your league has no active seasons, nothing will be displayed"""
        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return

        await self.league_standings.call(ctx)

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx, category='road', type='career'):
        """Displays a leaderboard of the users who have used `!saveid`.
        If the data is not up to date, try `!update` first.
        The categories are `road`, `oval`, `dirtroad`, and `dirtoval` and
        the types are `career` and `yearly`. Default is `road` `career`"""
        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return

        await self.leaderboard_db.call(ctx, category, type)

    @commands.command()
    async def iratings(self, ctx, category='road'):

        await self.iratings_db.call(ctx, category)

    @commands.command(name='allseries')
    async def allseries(self, ctx):
        """Show all series currently in iRacing to help with choosing your favorites for
        `!setfavseries`"""

        await self.all_series_db.call(ctx)

    @commands.command(name='addfavseries')
    async def addfavseries(self, ctx, series_id=None):
        """Use command `!allseries` to get a list of all series and ids.
            Then use this command `!addfavseries` with a list of comma
            separated ids to add your favorite series. This is identical
            to `setfavseries`"""
        if not series_id:
            await ctx.send('You must pass at least one series ID with this command. '
                           'Use `!help addfavseries` for more info.')

        await self.setfavseries(ctx, ids=str(series_id))

    @commands.command(name='setfavseries')
    async def setfavseries(self, ctx, *, ids=''):
        """Use command `!allseries` to get a list of all series and ids.
            Then use this command `!setfavseries` with a list of comma
            separated ids to add your favorite series. This is identical
            to `addfavseries`"""

        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return
        if ids == '':
            await ctx.send('You must pass at least one ID. Use `!help setfavseries` for more help')
            return

        await self.set_fav_series.call(ctx, ids)

    @commands.command(name='currentseries')
    async def currentseries(self, ctx):
        """Once you set favorites with `!setfavseries` or `!addfavseries` this command will
        show this and next week tracks for your favorite series"""

        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return
        await self.current_series_db.call(ctx)

    @commands.command(name='removefavseries')
    async def removefavseries(self, ctx, series_id=None):
        """Remove a series from your favorites list, use `!currentseries` to see
        what your current favorites are"""
        if not series_id:
            await ctx.send('You must pass a series ID with this command. Use `!help removefavseries` for more info.')

        if is_support_guild(ctx.guild.id):
            await ctx.send('Sorry, this discord does not allow update, saveid, '
                           'leaderboard, and series commands so as not to overload me. '
                           'Try `!careerstats` or `!yearlystats` with your customer ID to test '
                           'or go to #invite-link to bring the bot to your discord for all functionality')
            return

        await self.remove_fav_series.call(ctx, series_id)

    @commands.command(name='support')
    async def support(self, ctx):
        """Having issues with the bot? This will give you a link to the support server so you can ask for help"""
        await ctx.send('Join the support server here: https://discord.gg/bAq8Ec5JPQ')


def setup(bot):
    bot.add_cog(Iracing(bot))
