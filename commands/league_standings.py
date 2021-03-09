from ..models import Guild
import imgkit
from ..html_builder import *


class LeagueStandings:
    def __init__(self, pyracing, log):
        self.pyracing = pyracing
        self.log = log

    async def call(self, ctx):
        async with ctx.typing():
            guild = await Guild.get_or_none(discord_id=ctx.guild.id)
            if not guild:
                await self.send_error(ctx)
                return

            leagues = await guild.leagues.all()
            if not leagues:
                await self.send_error(ctx)
                return

            seasons = await self.active_seasons_from_leagues(leagues)
            await self.generate_and_send_season_images(ctx, seasons)

    async def active_seasons_from_leagues(self, leagues):
        seasons = []
        for league in leagues:
            async for season in league.seasons:
                if season.active > 0:
                    seasons.append(season)

        return seasons

    async def send_error(self, ctx):
        await ctx.send('Looks like something went wrong. '
                       'Make sure you have saved a league with `!saveleague`')

    def empty_standings(self, standings):
        for driver in standings.drivers:
            if driver.base_points > 0 or driver.total_points > 0:
                return False

        return True

    async def generate_and_send_season_images(self, ctx, seasons):
        for season in seasons:
            await self.build_season_table(ctx, season)

    async def build_season_table(self, ctx, season):
        league = await season.league
        try:
            standings = await self.pyracing.league_standings(league.iracing_id, season.iracing_id)
        except:
            return
        if not standings or not standings.drivers:
            return

        league_name = league.name
        title = f'{league.iracing_id} - {league_name} - {season.name} Standings'

        if self.empty_standings(standings):
            await ctx.send(f'{title} has empty standings')
            return

        table = PrettyTable()
        table.field_names = [
            '#', 'Driver', 'Nickname', 'Base Points', 'Total Points'
        ]

        drivers = sorted(standings.drivers, key=lambda x: x.position)
        for driver in drivers:
            table.add_row([
                str(driver.position),
                driver.display_name,
                driver.driver_nickname,
                driver.base_points,
                driver.total_points
            ])

        header_html_string = build_html_header_string(title)
        html_string = table.get_html_string(attributes={"id": "iracing_table"})
        css = wrap_in_style_tag(leaderboard_table_css + header_css)
        final_table_string = css + charset() + header_html_string + "\n" + html_string

        filename = f'league_season_{season.iracing_id}_standings.jpg'
        imgkit.from_string(final_table_string, filename)
        await ctx.send(file=discord.File(filename))
        cleanup_file(filename)
