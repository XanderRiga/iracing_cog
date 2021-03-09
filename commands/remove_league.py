from ..db_helpers import remove_league
import traceback
from ..models import Guild


class RemoveLeague:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, league_id):
        try:
            guild = await Guild.get(discord_id=str(ctx.guild.id))
            leagues = await guild.leagues.all()
            league_ids = map(lambda x: str(x.iracing_id), leagues)
            if league_id not in league_ids:
                await ctx.send('League ID must be a current favorite series. '
                               'Your current leagues can be found with `!leaguestandings`')
                return

            await remove_league(ctx.guild.id, league_id)
            await ctx.send(f'Successfully removed series: {league_id}')
        except:
            traceback.print_exc()
            await ctx.send('League ID must be a current favorite series. '
                           'Your current leagues can be found with `!leaguestandings`')
