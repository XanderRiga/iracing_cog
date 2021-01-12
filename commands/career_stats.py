from ..storage import *
from ..html_builder import *
import imgkit


class CareerStats:
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
                    await ctx.send('Please send an iRacing ID after the command or link your own with `!saveid <iRacing'
                                   ' ID>`')
                    return

            guild_dict = get_guild_dict(guild_id)
            career_stats = await self.update_user.update_career_stats(user_id, guild_dict, iracing_id)

            if career_stats:
                career_stats_html = get_career_stats_html(career_stats, iracing_id)
                filename = f'{iracing_id}_career_stats.jpg'
                imgkit.from_string(career_stats_html, filename)
                await ctx.send(file=discord.File(filename))
                cleanup_file(filename)
            else:
                await ctx.send('No career stats found for user: ' + str(iracing_id))
