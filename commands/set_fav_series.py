from ..helpers import *
from ..db_helpers import set_all_fav_series, init_tortoise, Tortoise
import traceback


class SetFavSeries:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, ids, all_series):
        try:
            id_list = ids.replace(' ', '').split(',')
            id_list = [x for x in id_list if x]
            try:
                parsed_ids = list(map(int, id_list))
                if not ids_valid_series(all_series, parsed_ids):
                    await ctx.send('Please enter a comma separated list of numbers which correspond to'
                                   'series IDs from the `!allseries` command')
                    return
                await init_tortoise()
                await set_all_fav_series(ctx.guild.id, parsed_ids)
                set_guild_favorites(ctx.guild.id, parsed_ids)
                await ctx.send(f'Successfully saved favorite series: {parsed_ids}')
                await Tortoise.close_connections()
            except ValueError:
                await ctx.send('Please enter a comma separated list of numbers which correspond to'
                               'series IDs from the `!allseries` command')
                await Tortoise.close_connections()
        except Exception:
            traceback.print_exc()
