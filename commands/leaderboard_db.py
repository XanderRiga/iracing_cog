from ..html_builder import *
import imgkit
from ..db_helpers import init_tortoise, Tortoise
from ..models import Driver, Guild, Category
import traceback


class LeaderboardDb:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, category, type):
        await self.delete_user_guild_relationships(ctx.guild)
        async with ctx.typing():
            if type not in ['career', 'yearly']:
                await ctx.send('Please try again with one of these types: `career`, `yearly`')
                return

            if category not in ['road', 'oval', 'dirtroad', 'dirtoval']:
                await ctx.send('Please try again with one of these categories: `road`, `oval`, `dirtroad`, `dirtoval`')
                return

            is_yearly = (type != 'career')

            try:
                guild = await Guild.get(discord_id=str(ctx.guild.id))
            except:
                await ctx.send('Looks like no one in this discord has data yet. '
                               'Try `!saveid` and `!update` to make sure at least one person is saved.')
                return

            drivers = await guild.drivers.all()
            table_html_string = await self.get_leaderboard_html_string(drivers, ctx.guild, Category.from_name(category),
                                                                       is_yearly)
            filename = f'{ctx.guild.id}_leaderboard.jpg'
            imgkit.from_string(table_html_string, filename)
            await ctx.send(file=discord.File(filename))

        cleanup_file(filename)

    async def get_leaderboard_html_string(self, drivers, guild, category, yearly=False):

        type_string = 'Yearly' if yearly else 'Career'
        header_string = 'iRacing ' + category.friendly_name() + ' ' + \
                        type_string + ' Leaderboard'

        table = PrettyTable()
        table.field_names = [
            '#', 'Discord Name', 'iRacing Name', 'Starts', 'Current iRating', 'Peak iRating', 'License', 'Wins',
            'Poles', 'Top 5s', 'Laps Led', 'Win %', 'Top 5 %', 'Laps Led %', 'Avg Incidents'
        ]

        drivers_with_ir = [(await x.current_irating_value(category), x) for x in drivers]
        drivers_with_ir.sort(reverse=True, key=lambda tup: tup[0])
        sorted_drivers = [x for key, x in drivers_with_ir]

        index = 1
        for driver in sorted_drivers:
            try:
                if yearly:

                    stat = await driver.current_year_stat(category)
                else:

                    stat = await driver.career_stat(category)


                current_ir = await driver.current_irating(category)

                peak_ir = await driver.peak_irating(category)

                license_class = await driver.current_license_class(category)

                if stat:
                    table.add_row(
                        [
                            index,
                            self.member_name(driver.discord_id, guild),
                            driver.iracing_name,
                            str(stat.total_starts),
                            str(current_ir.value) if current_ir else '1350',
                            str(peak_ir.value) if peak_ir else '1350',
                            str(license_class.class_letter()) + ' ' + str(license_class.safety_rating()) if
                            license_class else '',
                            str(stat.total_wins),
                            str(stat.poles),
                            str(stat.total_top_fives),
                            str(stat.laps_led),
                            str(stat.win_percentage) + '%',
                            str(stat.top_five_percentage) + '%',
                            str(stat.laps_led_percentage) + '%',
                            str(stat.avg_incidents),
                        ]
                    )
                    index += 1
            except Exception as e:
                traceback.print_exc()
                self.log.error(e)
                self.log.error(f'Error printing leaderboard data for user: {driver.name}')
                continue

        header_html_string = build_html_header_string(header_string)
        html_string = table.get_html_string(attributes={"id": "iracing_table"})
        css = wrap_in_style_tag(leaderboard_table_css + header_css)

        return css + charset() + header_html_string + "\n" + html_string

    def member_name(self, member_id, guild):
        member = discord.utils.find(lambda m: m.id == int(member_id), guild.members)
        if member:
            return member.name
        else:
            self.log.info('Could not find user for id: ' + str(member_id))
            return ''

    async def delete_user_guild_relationships(self, guild):
        current_member_ids = list(map(lambda x: str(x.id), guild.members))

        db_guild = await Guild.get(discord_id=guild.id)
        guild_drivers = await Driver.filter(guilds=db_guild)
        for driver in guild_drivers:
            if str(driver.discord_id) not in current_member_ids:

                await db_guild.drivers.remove(driver)
