from ..storage import *
from ..helpers import *


class AddFavSeries:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, series_id, all_series):
        try:
            series_id_int = int(series_id)
            if not ids_valid_series(all_series, [series_id_int]):
                await ctx.send('Series ID must be a number associated to a series in `!allseries`')
                return
            current_favorites = get_guild_favorites(ctx.guild.id)
            current_favorites = list(set(current_favorites))
            current_favorites.append(series_id_int)
            current_favorites.sort()
            set_guild_favorites(ctx.guild.id, current_favorites)
            await ctx.send(f'Successfully added series: {series_id}')
        except:
            await ctx.send('Series ID must be a number associated to a series in `!allseries`')
