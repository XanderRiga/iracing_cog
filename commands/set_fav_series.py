from ..helpers import *
from ..db_helpers import set_all_fav_series, init_tortoise, Tortoise
import traceback
from ..models import Series


class SetFavSeries:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, ids):
        try:
            id_list = ids.replace(' ', '').split(',')
            id_list = [x for x in id_list if x]
            try:
                parsed_ids = list(map(int, id_list))
                if not await are_valid_series(parsed_ids):
                    await ctx.send('Please enter a comma separated list of numbers which correspond to'
                                   'series IDs from the `!allseries` command')
                    return

                await set_all_fav_series(ctx.guild.id, parsed_ids)
                await ctx.send(f'Successfully saved favorite series: {parsed_ids}')
            except ValueError:
                await ctx.send('Please enter a comma separated list of numbers which correspond to'
                               'series IDs from the `!allseries` command')
        except Exception:
            traceback.print_exc()
