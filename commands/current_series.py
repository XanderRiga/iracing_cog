from ..storage import *
from ..html_builder import *
import imgkit


class CurrentSeries:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, all_series):
        favorites = get_guild_favorites(ctx.guild.id)
        if not favorites:
            await ctx.send('Follow the directions by calling `!setfavseries` to set favorite'
                           'series before ')
            return

        series = series_from_ids(favorites, all_series)
        if not series:
            await ctx.send('Series not found, wait a minute and try again or contact an admin.')

        race_week = series[0].race_week - 1  # This is 1 indexed for some reason, but the tracks aren't
        this_week_string = build_race_week_string(race_week, series, 'This Week', self.log)
        next_week_string = build_race_week_string(race_week + 1, series, 'Next Week', self.log)

        this_week_filename = f'{ctx.guild.id}_this_week.jpg'
        next_week_filename = f'{ctx.guild.id}_next_week.jpg'
        imgkit.from_string(this_week_string, this_week_filename)
        imgkit.from_string(next_week_string, next_week_filename)
        await ctx.send(file=discord.File(this_week_filename))
        await ctx.send(file=discord.File(next_week_filename))
        cleanup_file(this_week_filename)
        cleanup_file(next_week_filename)
