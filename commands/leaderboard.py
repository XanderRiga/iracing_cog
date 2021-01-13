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
            table_html_string = self.get_leaderboard_html_string(leaderboard_data, ctx.guild, category, self.log, is_yearly)
            filename = f'{ctx.guild.id}_leaderboard.jpg'
            imgkit.from_string(table_html_string, filename)
            await ctx.send(file=discord.File(filename))

        cleanup_file(filename)

    def get_leaderboard_html_string(self, user_data_list, guild, category, log, yearly=False):
        type_string = 'Yearly' if yearly else 'Career'
        minutes_since_update = minutes_since_last_update(guild.id, log)
        time_since_update_string = f' - Last updated {minutes_since_update} minute(s) ago' if minutes_since_update \
            else ''
        header_string = 'iRacing ' + lowercase_to_readable_categories(category) + ' ' + \
                        type_string + ' Leaderboard' + time_since_update_string

        table = PrettyTable()
        table.field_names = [
            '#', 'Discord Name', 'iRacing Name', 'Starts', 'Current iRating', 'Peak iRating', 'License', 'Wins',
            'Top 5s', 'Laps Led', 'Win %', 'Top 5 %', 'Laps Led %', 'Avg Incidents'
        ]

        for index, item in enumerate(user_data_list, start=1):
            try:
                member_id = item[0]
                member_data = item[-1]

                stats_list = self.stats_list(yearly, member_data)
                career_stats = self.career_stats(category, stats_list)

                if career_stats:
                    table.add_row(
                        [
                            index,
                            self.member_name(member_id, guild),
                            self.iracing_name(member_data),
                            str(career_stats['starts']),
                            str(self.irating(category, member_data)),
                            str(self.peak_irating(category, member_data)),
                            str(self.license_class(category, member_data)),
                            str(career_stats['wins']),
                            str(career_stats['top_5s']),
                            str(career_stats['laps_led']),
                            str(career_stats['win_pcnt']) + '%',
                            str(career_stats['top_5_pcnt']) + '%',
                            str(career_stats['laps_led_pcnt']) + '%',
                            str(career_stats['incidents_avg']),
                        ]
                    )
            except Exception as e:
                log.error(e)
                log.error(f'Error printing leaderboard data for user: {item}')
                continue

        header_html_string = build_html_header_string(header_string)
        html_string = table.get_html_string(attributes={"id": "iracing_table"})
        css = wrap_in_style_tag(leaderboard_table_css + header_css)

        return css + header_html_string + "\n" + html_string

    def member_name(self, member_id, guild):
        member = discord.utils.find(lambda m: m.id == int(member_id), guild.members)
        if member:
            return member.name
        else:
            self.log.info('Could not find user for id: ' + str(member_id))
            return ''

    def stats_list(self, yearly, member_data):
        if yearly:
            return get_current_year_stats(member_data['yearly_stats'])
        else:
            return member_data['career_stats']

    def irating(self, category, member_data):
        irating = 0
        if category == 'road':
            irating = member_data['road_irating'][-1][1]
        elif category == 'oval':
            irating = member_data['oval_irating'][-1][1]
        elif category == 'dirtroad':
            irating = member_data['dirt_road_irating'][-1][1]
        elif category == 'dirtoval':
            irating = member_data['dirt_oval_irating'][-1][1]

        return irating

    def peak_irating(self, category, member_data):
        peak_irating = 1350
        if category == 'road':
            peak_irating = peak_irating_value(member_data['road_irating'])
        elif category == 'oval':
            peak_irating = peak_irating_value(member_data['oval_irating'])
        elif category == 'dirtroad':
            peak_irating = peak_irating_value(member_data['dirt_road_irating'])
        elif category == 'dirtoval':
            peak_irating = peak_irating_value(member_data['dirt_oval_irating'])

        return peak_irating

    def license_class(self, category, member_data):
        license_class = 'N/A'
        if category == 'road':
            license_class = member_data['road_license_class']
        elif category == 'oval':
            license_class = member_data['oval_license_class']
        elif category == 'dirtroad':
            license_class = member_data['dirt_road_license_class']
        elif category == 'dirtoval':
            license_class = member_data['dirt_oval_license_class']

        return license_class

    def iracing_name(self, member_data):
        iracing_name = ''
        if 'name' in member_data:
            iracing_name = member_data['name']

        return iracing_name

    def career_stats(self, category, stats_list):
        career_stats = None
        for stat in stats_list:
            if category == 'road':
                if stat['category'] == 'Road':
                    career_stats = stat
            elif category == 'oval':
                if stat['category'] == 'Oval':
                    career_stats = stat
            elif category == 'dirtroad':
                if stat['category'] == 'Dirt Road':
                    career_stats = stat
            elif category == 'dirtoval':
                if stat['category'] == 'Dirt Oval':
                    career_stats = stat

        return career_stats

