from ..storage import *
from ..db_helpers import remove_fav_series, init_tortoise, Tortoise
import traceback


class RemoveFavSeries:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, series_id):
        try:
            series_id_int = int(series_id)
            current_favorites = get_guild_favorites(ctx.guild.id)
            if series_id_int not in current_favorites:
                await ctx.send('Series ID must be a current favorite series. '
                               'Your current favorites can be found with `!currentseries`')
                return
            current_favorites.remove(series_id_int)

            await init_tortoise()
            await remove_fav_series(ctx.guild.id, series_id)
            set_guild_favorites(ctx.guild.id, current_favorites)
            await ctx.send(f'Successfully removed series: {series_id}')
            await Tortoise.close_connections()
        except:
            traceback.print_exc()
            await ctx.send('Series ID must be a current favorite series. '
                           'Your current favorites can be found with `!currentseries`')
            await Tortoise.close_connections()
