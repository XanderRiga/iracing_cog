from ..db_helpers import *
from traceback import print_exc


class SaveName:
    def __init__(self, pyracing, log):
        self.pyracing = pyracing
        self.log = log

    async def call(self, ctx, iracing_name):
        try:
            driver_stats_list = await self.pyracing.driver_stats(search=iracing_name)
        except:
            await self.send_error_message(ctx)
            return

        if not driver_stats_list:
            await self.send_error_message(ctx)
            return

        queried_driver = driver_stats_list[0]
        if not queried_driver.display_name.lower() == iracing_name.lower():
            await self.send_error_message(ctx)
            return

        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        await create_or_update_driver(queried_driver.cust_id, user_id, guild_id, queried_driver.display_name)
        await ctx.send('iRacing Name and ID successfully saved. Use `!update` to see this user on the leaderboard.')

    async def send_error_message(self, ctx):
        await ctx.send('Driver could not be found. '
                       'Make sure you type the name exactly how it looks on iRacing, including any numbers. '
                       'If it still is not working, check if iRacing is down or '
                       'try using `!saveid` to save your ID directly.')
