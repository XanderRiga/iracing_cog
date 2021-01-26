from ..html_builder import *
from ..helpers import cleanup_file
import imgkit
from pyvirtualdisplay import Display


class AllSeries:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, all_series):
        road, oval, dirt_road, dirt_oval = [], [], [], []
        for season in all_series:
            if season.cat_id == 2:
                road.append(season)
            if season.cat_id == 1:
                oval.append(season)
            if season.cat_id == 4:
                dirt_road.append(season)
            if season.cat_id == 3:
                dirt_oval.append(season)

        html_strings = [
            build_series_html_string(road, 'Road Series'),
            build_series_html_string(oval, 'Oval Series'),
            build_series_html_string(dirt_road, 'Dirt Road Series'),
            build_series_html_string(dirt_oval, 'Dirt Oval Series')
        ]

        for string in html_strings:
            filename = f'{ctx.guild.id}_series.jpg'
            display = Display(visible=0, size=(600,600))
            display.start()        
            imgkit.from_string(string, filename)
            await ctx.send(file=discord.File(filename))
            cleanup_file(filename)
            display.stop()