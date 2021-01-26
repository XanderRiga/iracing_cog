from ..storage import *
from ..html_builder import *
import imgkit
from pyvirtualdisplay import Display


class YearlyStats:
    def __init__(self, pyracing, log, update_user):
        self.pyracing = pyracing
        self.log = log
        self.update_user = update_user

    async def call(self, ctx, iracing_id):
        async with ctx.typing():
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            if not iracing_id:
                iracing_id = get_user_iracing_id(user_id, guild_id)
                if not iracing_id:
                    await ctx.send('Please send an iRacing ID after the command or link your own with '
                                   '`!saveid <iRacing ID>`')
                    return

            guild_dict = get_guild_dict(guild_id)
            yearly_stats = await self.update_user.update_yearly_stats(user_id, guild_dict, iracing_id)

            if yearly_stats:
                yearly_stats_html = get_yearly_stats_html(yearly_stats, iracing_id)
                filename = f'{iracing_id}_yearly_stats.jpg'
            	display = Display(visible=0, size=(600,600))
            	display.start()    
                imgkit.from_string(yearly_stats_html, filename)
                await ctx.send(file=discord.File(filename))
                cleanup_file(filename)
            	display.stop()
            else:
                await ctx.send('No yearly stats found for user: ' + str(iracing_id))
