from ..html_builder import *
from ..helpers import *
import imgkit
from bokeh.plotting import figure, output_file, save
from bokeh.io import export_png
from bokeh.palettes import Category20
from bokeh.models import Legend
import itertools
from selenium import webdriver
from datetime import datetime
from ..queries.irating_dicts import get_irating_dicts
from ..db_helpers import Guild
from ..models import Category


class IratingsDb:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, category):
        async with ctx.typing():
            if category not in ['road', 'oval', 'dirtroad', 'dirtoval']:
                ctx.send('The category should be one of `road`, `oval`, `dirtroad`, `dirtoval`')
                return

            try:

                guild = await Guild.get(discord_id=str(ctx.guild.id))
            except:
                await ctx.send('Looks like no one in this discord has data yet. '
                               'Try `!saveid` and `!update` to make sure at least one person is saved.')
                return

            category_model = Category.from_name(category)

            today = datetime.now()
            date_6mo_ago = six_months_before(today)

            p = figure(
                title=f'{category_model.friendly_name()} iRatings',
                x_axis_type='datetime',
                x_range=(date_6mo_ago, datetime.now())
            )
            p.toolbar.logo = None
            p.toolbar_location = None
            legend = Legend(location=(0, -10))
            p.add_layout(legend, 'right')
            output_file('output_iratings.html')

            colors = itertools.cycle(Category20[20])

            irating_dicts = await get_irating_dicts(guild, category_model)
            for irating_dict in irating_dicts:
                for user_id, iratings_list in irating_dict.items():
                    member = ctx.guild.get_member(int(user_id))
                    datetimes = []
                    iratings = []
                    for irating in iratings_list:
                        datetimes.append(irating.datetime())
                        iratings.append(irating.value)

                    p.line(
                        datetimes,
                        iratings,
                        legend_label=member.display_name,
                        line_width=2,
                        color=next(colors)
                    )

            filename = f'irating_graph_{ctx.guild.id}.png'
            export_png(p, filename=filename, webdriver=webdriver.Chrome(options=self.webdriver_options()))
            await ctx.send(file=discord.File(filename))
            cleanup_file(filename)

    def webdriver_options(self):
        options = webdriver.chrome.options.Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--headless")
        options.add_argument("--hide-scrollbars")
        return options
