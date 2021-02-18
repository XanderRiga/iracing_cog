from ..html_builder import *
import imgkit
from ..db_helpers import init_tortoise
from tortoise import Tortoise
from ..models import Stat, Driver, StatsType, Category


class CareerStatsDb:
    def __init__(self, pyracing, log):
        self.pyracing = pyracing
        self.log = log

    async def call(self, ctx, iracing_id):
        try:
            async with ctx.typing():
                user_id = str(ctx.author.id)
                if not iracing_id:
                    try:

                        driver = await Driver.get(discord_id=user_id)
                        iracing_id = driver.iracing_id
                        if not iracing_id:
                            await ctx.send('Please send an iRacing ID after the command or '
                                           'link your own with `!saveid`')
                            return
                    except:
                        await ctx.send('Please send an iRacing ID after the command or '
                                       'link your own with `!saveid`')
                        return

                try:

                    driver = await Driver.get(iracing_id=iracing_id)
                    career_stats = await Stat.filter(driver=driver, stat_type=StatsType.career)
                except:
                    career_stats = await self.build_stats(iracing_id)

                if career_stats:
                    career_stats_html = get_career_stats_html_db(career_stats, iracing_id)
                    filename = f'{iracing_id}_career_stats.jpg'
                    imgkit.from_string(career_stats_html, filename)
                    await ctx.send(file=discord.File(filename))
                    cleanup_file(filename)
                else:
                    await ctx.send('No career stats found for user: ' + str(iracing_id))
        except Exception as e:
            self.log.info(f'Failed career stats(db) for {ctx}, exception: {e}')

    async def build_stats(self, iracing_id):
        """When we get a query for a user not in our DB, we have to do an API request"""
        career_stats_list = await self.pyracing.career_stats(iracing_id)
        stat_model_list = []
        for stat in career_stats_list:
            stat_model_list.append(Stat(
                category=Category.from_name(stat.category),
                stat_type=StatsType.career,
                avg_incidents=stat.incidents_avg,
                total_laps=stat.laps,
                laps_led=stat.laps_led,
                laps_led_percentage=stat.laps_led_pcnt,
                points_avg=stat.points_avg,
                points_club=stat.points_club,
                poles=stat.poles,
                avg_start_pos=stat.pos_start_avg,
                avg_finish_pos=stat.pos_finish_avg,
                total_starts=stat.starts,
                top_five_percentage=stat.top_5_pcnt,
                total_top_fives=stat.top_5s,
                win_percentage=stat.win_pcnt,
                total_wins=stat.wins
            ))

        return stat_model_list
