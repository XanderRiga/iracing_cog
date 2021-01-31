from ..storage import *
from ..helpers import *
from ..db_helpers import add_fav_series, init_tortoise, Tortoise
from ..models import Series


class AddFavSeries:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, series_id):
        try:
            series_id_int = int(series_id)
            if not await are_valid_series([series_id_int]):
                await ctx.send('Series ID must be a number associated to a series in `!allseries`')
                return
            current_favorites = get_guild_favorites(ctx.guild.id)
            current_favorites = list(set(current_favorites))
            current_favorites.append(series_id_int)
            current_favorites.sort()

            await add_fav_series(ctx.guild.id, series_id)
            set_guild_favorites(ctx.guild.id, current_favorites)
            await ctx.send(f'Successfully added series: {series_id}')
            await Tortoise.close_connections()
        except:
            await ctx.send('Series ID must be a number associated to a series in `!allseries`')
            await Tortoise.close_connections()
