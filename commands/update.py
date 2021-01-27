from datetime import datetime
from ..storage import *
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
        guild_id = str(ctx.guild.id)
        guild_dict = get_guild_dict(guild_id)
        user_id = str(ctx.author.id)

        start_time = datetime.now()
        dt_string = start_time.strftime("%d/%m/%Y %H:%M:%S")
        self.log.info(f'=============== Manual update for {ctx.author.name} update started at: ' +
                      dt_string + ' ======================')

        await ctx.send(f'Updating user: {ctx.author.name}, this may take a minute')
        if 'iracing_id' in guild_dict[user_id]:
            guild_dict = await self.update_user.update_user_in_dict(user_id, guild_dict, guild_id)

        set_guild_data(guild_id, guild_dict)
        self.log.info(f'=============== Manual update for {ctx.author.name} finished that started at: ' +
                      dt_string + ' ======================')
        finish_time = datetime.now()
        self.log.info(f'=============== Manual update for {ctx.author.name} took ' + str(
            (finish_time - start_time).total_seconds()) + ' seconds ===============')
        await ctx.send(f'Successfully updated {ctx.author.name}')

    async def update_server(self, ctx):
        start_time = datetime.now()
        dt_string = start_time.strftime("%d/%m/%Y %H:%M:%S")
        self.log.info('=============== Manual update started at: ' + dt_string + ' ======================')

        await ctx.send("Updating all users in this server, this may take a few minutes")
        guild_id = str(ctx.guild.id)
        guild_dict = get_guild_dict(guild_id)
        for user_id in guild_dict:
            if 'iracing_id' in guild_dict[user_id]:
                guild_dict = await self.update_user.update_user_in_dict(user_id, guild_dict, guild_id)

        set_guild_data(guild_id, guild_dict)
        self.log.info(
            '=============== Manual update finished that started at: ' + dt_string + ' ======================')
        finish_time = datetime.now()
        self.log.info('=============== Manual update took ' + str(
            (finish_time - start_time).total_seconds()) + ' seconds ===============')
        await ctx.send("Successfully updated this server")

    async def update_all_servers(self, all_series):
        start_time = time.monotonic()
        self.log.info('=============== Updating all servers stats ======================')

        try:
            await generate_schemas()
            for series in all_series:
                try:
                    await get_or_create_series(series)
                    await get_or_create_season(series)
                except Exception as e:
                    print(traceback.format_exc())
                    self.log.warning(f'Failed saving season/series: {series}, exception: {e}')
        except Exception as e:
            self.log.warning(f'Failed loading all series {str(e)}')

        guilds = []
        for file in os.scandir(folder):
            if file.path.endswith('.json'):
                guilds.append(os.path.basename(file.path)[:-5])

        self.log.info(f'Updating {len(guilds)} total guilds')
        for guild_id in guilds:
            await self.update_server_background(guild_id)

        self.log.info('=============== Auto update for all servers took ' + str(
            (time.monotonic() - start_time)) + ' seconds =================')

    async def update_server_background(self, guild_id):
        start_time = datetime.now()
        dt_string = start_time.strftime("%d/%m/%Y %H:%M:%S")
        guild_id = str(guild_id)
        self.log.info(f'=============== background update for guild: {guild_id} started at: ' +
                      dt_string + ' ======================')

        guild_dict = get_guild_dict(guild_id)
        for user_id in guild_dict:
            if 'iracing_id' in guild_dict[user_id]:
                guild_dict = await self.update_user.update_user_in_dict(user_id, guild_dict, guild_id)

        set_guild_data(guild_id, guild_dict)
        finish_time = datetime.now()
        self.log.info(f'=============== Auto update for guild: {guild_id} took ' + str(
            (finish_time - start_time).total_seconds()) + ' seconds ===============')
