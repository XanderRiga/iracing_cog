from ..storage import *
from ..html_builder import *
from ..helpers import delete_missing_users, get_relevant_leaderboard_data
import imgkit


class Leaderboard:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, category, type):
        delete_missing_users(ctx.guild)
        async with ctx.typing():
            if type not in ['career', 'yearly']:
                await ctx.send('Please try again with one of these types: `career`, `yearly`')
                return

            if category not in ['road', 'oval', 'dirtroad', 'dirtoval']:
                await ctx.send('Please try again with one of these categories: `road`, `oval`, `dirtroad`, `dirtoval`')
                return

            is_yearly = (type != 'career')

            guild_dict = get_guild_dict(ctx.guild.id)
            leaderboard_data = get_relevant_leaderboard_data(guild_dict, category)
            table_html_string = get_leaderboard_html_string(leaderboard_data, ctx.guild, category, self.log, is_yearly)
            filename = f'{ctx.guild.id}_leaderboard.jpg'
            imgkit.from_string(table_html_string, filename)
            await ctx.send(file=discord.File(filename))
            cleanup_file(filename)
