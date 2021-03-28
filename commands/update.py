import time
import asyncio
from ..db_helpers import *
import traceback


class Update:
    def __init__(self, pyracing, log, update_user):
        self.update_user = update_user
        self.pyracing = pyracing
        self.log = log

    async def update_member(self, ctx):
        driver = await Driver.get_or_none(discord_id=ctx.author.id)
        if not driver:
            await ctx.send('Save your id with `!saveid` before calling this method')
            return

        start_time = datetime.now()
        dt_string = start_time.strftime("%d/%m/%Y %H:%M:%S")
        self.log.info(f'=============== Manual update for {ctx.author.name} update started at: ' +
                      dt_string + ' ======================')
        await self.update_user.update_fields(driver)
        await ctx.send(f'Successfully updated {ctx.author.name}')

        self.log.info(f'=============== Manual update for {ctx.author.name} finished that started at: ' +
                      dt_string + ' ======================')
        finish_time = datetime.now()
        self.log.info(f'=============== Manual update for {ctx.author.name} took ' + str(
            (finish_time - start_time).total_seconds()) + ' seconds ===============')

    async def update_all_servers(self):
        start_time = time.monotonic()
        self.log.info('=============== Updating all servers stats ======================')
        await generate_schemas()

        guilds = await Guild.all()

        self.log.info(f'Updating {len(guilds)} total guilds')
        for guild in guilds:
            try:
                await self.update_server_background(guild)
            except Exception as e:
                self.log.warning(f'Guild failed update: {guild.id} skipping')

        self.log.info('=============== Auto update for all servers took ' + str(
            (time.monotonic() - start_time)) + ' seconds =================')

    async def update_series(self):
        await generate_schemas()

        all_series = await self.pyracing.current_seasons(series_id=True)
        try:
            for series in all_series:
                try:
                    await get_or_create_series(series)
                    await get_or_create_season(series)
                except Exception as e:
                    print(traceback.format_exc())
                    self.log.warning(f'Failed saving season/series: {series}, exception: {e}')
        except Exception as e:
            self.log.warning(f'Failed loading all series {str(e)}')

    async def update_server_background(self, guild):
        start_time = datetime.now()
        dt_string = start_time.strftime("%d/%m/%Y %H:%M:%S")
        guild_id = str(guild.discord_id)
        self.log.info(f'=============== background update for guild: {guild_id} started at: ' +
                      dt_string + ' ======================')

        async for driver in guild.drivers:
            try:
                await self.update_user.update_fields(driver)
            except:
                self.log.warning(f'Driver failed update: {driver.id} skipping')

        finish_time = datetime.now()
        self.log.info(f'=============== Auto update for guild: {guild_id} took ' + str(
            (finish_time - start_time).total_seconds()) + ' seconds ===============')
