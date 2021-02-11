from ..storage import *
from ..db_helpers import remove_fav_series, init_tortoise, Tortoise
import traceback
from ..models import Guild


class RemoveFavSeries:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, series_id):
        try:
            await init_tortoise()
            guild = await Guild.get(discord_id=str(ctx.guild.id))
            await init_tortoise()
            current_favorites = await guild.favorite_series.all()
            favorite_ids = map(lambda x: str(x.iracing_id), current_favorites)
            if series_id not in favorite_ids:
                await ctx.send('Series ID must be a current favorite series. '
                               'Your current favorites can be found with `!currentseries`')
                return

            await init_tortoise()
            await remove_fav_series(ctx.guild.id, series_id)
            await ctx.send(f'Successfully removed series: {series_id}')
            await Tortoise.close_connections()
        except:
            traceback.print_exc()
            await ctx.send('Series ID must be a current favorite series. '
                           'Your current favorites can be found with `!currentseries`')
            await Tortoise.close_connections()
