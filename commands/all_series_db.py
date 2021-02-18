from ..html_builder import *
from ..helpers import cleanup_file
import imgkit
from ..db_helpers import init_tortoise, Tortoise
from ..models import Series


class AllSeriesDb:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx):
        road_series = await Series.filter(category=Category.road)
        oval_series = await Series.filter(category=Category.oval)
        dirt_road_series = await Series.filter(category=Category.dirt_road)
        dirt_oval_series = await Series.filter(category=Category.dirt_oval)

        html_strings = [
            build_series_model_html_string(road_series, 'Road Series'),
            build_series_model_html_string(oval_series, 'Oval Series'),
            build_series_model_html_string(dirt_road_series, 'Dirt Road Series'),
            build_series_model_html_string(dirt_oval_series, 'Dirt Oval Series')
        ]

        for string in html_strings:
            filename = f'{ctx.guild.id}_series.jpg'
            imgkit.from_string(string, filename)
            await ctx.send(file=discord.File(filename))
            cleanup_file(filename)
