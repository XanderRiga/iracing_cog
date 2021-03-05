from ..models import League, LeagueSeason
from ..db_helpers import get_or_create_guild


class SaveLeague:
    def __init__(self, pyracing, log):
        self.pyracing = pyracing
        self.log = log

    async def call(self, ctx, league_id):
        try:
            league_seasons = await self.pyracing.league_seasons(league_id)
        except:
            await self.send_error_message(ctx)
            return

        if not league_seasons:
            await self.send_error_message(ctx)
            return

        guild = await get_or_create_guild(ctx.guild.id)

        league = await self.build_league(guild, league_id)
        await self.build_league_seasons(league, league_seasons)
        await ctx.send('Successfully saved league')

    async def build_league_seasons(self, league, league_seasons):
        for season in league_seasons:
            await LeagueSeason.get_or_create(
                iracing_id=season.season_id,
                defaults={
                    'league': league,
                    'name': season.league_season_name,
                    'active': season.active,
                    'league_points_system_description': season.league_points_system_description,
                    'league_points_system_name': season.league_points_system_name
                }
            )

    async def build_league(self, guild, league_id):
        league_tuple = await League.get_or_create(iracing_id=league_id)
        league = league_tuple[0]

        await league.guilds.add(guild)
        return league_tuple[0]

    async def send_error_message(self, ctx):
        await ctx.send('League could not be found, '
                       'make sure the league id is correct.'
                       'The league ID can be found by navigating to '
                       'the league home page on iRacing, the URL will have `league=ID` '
                       'where ID is the league ID you can enter')
