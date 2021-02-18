from ..html_builder import *
from ..helpers import *
import imgkit
from ..db_helpers import Driver


class RecentRaces:
    def __init__(self, pyracing, log):
        self.pyracing = pyracing
        self.log = log

    async def call(self, ctx, iracing_id):
        async with ctx.typing():
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            if not iracing_id:
                try:

                    driver = await Driver.get(discord_id=user_id)
                    iracing_id = driver.iracing_id
                except:
                    pass
                if not iracing_id:
                    await ctx.send('Please send an iRacing ID with the command or link your own with `!saveid <iRacing '
                                   'ID>`')
                    return

            races_stats_list = await self.pyracing.last_races_stats(iracing_id)
            if races_stats_list:
                table_html_string = await recent_races_table_db_string(races_stats_list, iracing_id)
                filename = f'{guild_id}_{iracing_id}_recent_races.jpg'
                imgkit.from_string(table_html_string, filename)
                await ctx.send(file=discord.File(filename))
                cleanup_file(filename)
            else:
                await ctx.send('Recent races not found for user: ' + iracing_id)
