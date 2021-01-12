from datetime import datetime
from .update_user import UpdateUser
from ..storage import *


class Update:
    def __init__(self, pyracing, log):
        self.update_user = UpdateUser(pyracing, log)
        self.pyracing = pyracing
        self.log = log

    async def update(self, ctx):
        start_time = datetime.now()
        dt_string = start_time.strftime("%d/%m/%Y %H:%M:%S")
        self.log.info('=============== Manual update started at: ' + dt_string + ' ======================')

        await ctx.send("Updating all users in this server, this may take a few minutes")
        guild_id = str(ctx.guild.id)
        guild_dict = get_guild_dict(guild_id)
        for user_id in guild_dict:
            if 'iracing_id' in guild_dict[user_id]:
                guild_dict = await self.update_user.update_user_in_dict(user_id, guild_dict)

        set_guild_data(guild_id, guild_dict)
        self.log.info('=============== Manual update finished that started at: ' + dt_string + ' ======================')
        finish_time = datetime.now()
        self.log.info('=============== Manual update took ' + str(
            (finish_time - start_time).total_seconds()) + ' seconds ===============')
        await ctx.send("Successfully updated this server")

    async def update_all_servers(self):
        start_time = datetime.now()
        dt_string = start_time.strftime("%d/%m/%Y %H:%M:%S")
        self.log.info('=============== Updating all user stats: ' + dt_string + ' ======================')

        guilds = []
        for file in os.scandir(folder):
            if file.path.endswith('.json'):
                guilds.append(os.path.basename(file.path)[:-5])

        for guild_id in guilds:
            guild_dict = get_guild_dict(guild_id)
            for user_id in guild_dict:
                if 'iracing_id' in guild_dict[user_id]:
                    guild_dict = await self.update_user.update_user_in_dict(user_id, guild_dict)

            set_guild_data(guild_id, guild_dict)

        self.log.info('=============== Finished update that started at: ' + dt_string + ' ======================')
        finish_time = datetime.now()
        self.log.info('=============== Auto update took ' + str(
            (finish_time - start_time).total_seconds()) + ' seconds =================')