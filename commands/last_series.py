from ..storage import *
from ..html_builder import *
import imgkit


class LastSeries:
    def __init__(self, pyracing, log):
        self.pyracing = pyracing
        self.log = log

    async def call(self, ctx, iracing_id):
        async with ctx.typing():
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            if not iracing_id:
                iracing_id = get_user_iracing_id(user_id, guild_id)
                if not iracing_id:
                    await ctx.send('Please send an iRacing ID with the command or link your own with `!saveid <iRacing '
                                   'ID>`')
                    return

            last_series = await self.pyracing.last_series(iracing_id)

            if last_series:
                table_html_string = get_last_series_html_string(last_series, iracing_id)
                filename = f'{guild_id}_{iracing_id}_last_series.jpg'
                imgkit.from_string(table_html_string, filename)
                await ctx.send(file=discord.File(filename))
                cleanup_file(filename)
            else:
                await ctx.send('Recent races not found for user: ' + iracing_id)
