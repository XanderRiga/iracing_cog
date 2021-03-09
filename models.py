from tortoise import fields
from tortoise.models import Model
from enum import IntEnum
from datetime import datetime, timezone
from typing import Optional


class LicenseClass(IntEnum):
    R = 1
    D = 2
    C = 3
    B = 4
    A = 5
    P = 6
    PWC = 7


class Category(IntEnum):
    oval = 1
    road = 2
    dirt_oval = 3
    dirt_road = 4

    def friendly_name(self):
        if self.value == 1:
            return 'Oval'
        elif self.value == 2:
            return 'Road'
        elif self.value == 3:
            return 'Dirt Oval'
        elif self.value == 4:
            return 'Dirt Road'
        else:
            return ''

    @staticmethod
    def from_name(name):
        lower_name = name.lower()
        if lower_name == 'oval':
            return Category.oval
        if lower_name == 'road':
            return Category.road
        if lower_name == 'dirt road' or lower_name == 'dirtroad' or lower_name == 'dirt_road':
            return Category.dirt_road
        if lower_name == 'dirt oval' or lower_name == 'dirtoval' or lower_name == 'dirt_oval':
            return Category.dirt_oval
        else:
            return None


class StatsType(IntEnum):
    career = 0
    yearly = 1


class Base(Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Irating(Base):
    value = fields.IntField()
    timestamp = fields.TextField()
    driver = fields.ForeignKeyField('models.Driver', related_name='iratings')
    category: Category = fields.IntEnumField(Category)

    def datetime(self):
        try:
            return datetime.strptime(self.timestamp, '%Y-%m-%d %H:%M:%S')
        except Exception:
            return None

    def __str__(self):
        return f'{self.driver.discord_id} irating for {self.category} at {self.timestamp}'


# LicenseClass is in the format `4368` where the first digit represents the
# license class A through Rookie which can be seen in Constants.
# License and the next 3 digits are the actual rating, so the example '4368'
# would be B class with a 3.68 rating
class License(Base):
    license_number = fields.IntField()
    timestamp = fields.TextField()
    driver = fields.ForeignKeyField('models.Driver', related_name='licenses')
    category: Category = fields.IntEnumField(Category)

    # 1, 2, 3, 4, 5
    def class_number(self) -> int:
        return int(str(self.license_number)[0])

    # A, B, C, D, R
    def class_letter(self) -> str:
        return LicenseClass(self.class_number()).name

    # example: 3.15
    def safety_rating(self) -> str:
        relevant_chars = str(self.license_number)[1:]
        return relevant_chars[0] + '.' + relevant_chars[1:]


class Driver(Base):
    iratings: fields.ReverseRelation["Irating"]
    licenses: fields.ReverseRelation["Driver"]
    stats: fields.ReverseRelation["Stat"]
    discord_id = fields.CharField(max_length=30, unique=True)
    guilds: fields.ManyToManyRelation["Guild"] = fields.ManyToManyField(
        "models.Guild", related_name="drivers", through="driver_guild"
    )
    iracing_name = fields.TextField(null=True)
    iracing_id = fields.TextField(null=True)

    async def iratings_by_category(self, category):
        return await self.iratings.filter(category=category)

    async def peak_irating(self, category) -> Optional[Irating]:
        try:
            relevant_iratings = await self.iratings_by_category(category)
            return await max(relevant_iratings, key=lambda irating: irating.value)
        except:
            return None

    async def peak_irating_value(self, category) -> int:
        try:
            peak_irating_model = await self.peak_irating(category)
            if peak_irating_model:
                return peak_irating_model.value
            else:
                return 1350
        except:
            return 1350

    async def current_irating(self, category) -> Optional[Irating]:
        try:
            relevant_iratings = await self.iratings_by_category(category)
            return await max(relevant_iratings, key=lambda irating: irating.timestamp)
        except:
            return None

    async def current_irating_value(self, category) -> int:
        try:
            current_irating_model = await self.current_irating(category)
            return current_irating_model.value
        except:
            return 1350

    async def current_license_class(self, category):
        try:
            licenses = await self.licenses.filter(category=category)
            return await max(licenses, key=lambda license: license.timestamp)
        except:
            return None

    async def current_year_stat(self, category):
        today = datetime.today()
        try:
            return await Stat.get(
                category=category,
                stat_type=StatsType.yearly,
                year=today.year,
                driver=self
            )
        except:
            return None

    async def career_stat(self, category):
        try:
            return await Stat.get(
                category=category,
                stat_type=StatsType.career,
                driver=self
            )
        except:
            return None

    def __str__(self):
        return self.iracing_name


class Guild(Base):
    discord_id = fields.CharField(max_length=30, unique=True)
    favorite_series: fields.ManyToManyRelation["Series"] = fields.ManyToManyField(
        "models.Series", related_name="guilds", through="favorite_series"
    )
    leagues: fields.ManyToManyRelation["League"]
    drivers: fields.ManyToManyRelation[Driver]


class Track(Base):
    iracing_id = fields.CharField(max_length=30)
    name = fields.TextField()


class Series(Base):
    iracing_id = fields.CharField(max_length=30, unique=True)
    favorited_guilds: fields.ManyToManyRelation[Guild]
    seasons: fields.ReverseRelation["Season"]
    name = fields.TextField()
    category: Category = fields.IntEnumField(Category)

    async def current_season(self):
        all_seasons = await self.seasons.all()
        most_recent = all_seasons[0]
        for season in all_seasons:
            if season.start_time > most_recent.start_time:
                most_recent = season

        return most_recent


class Season(Base):
    season_combos: fields.ReverseRelation["SeasonCombo"]
    iracing_id = fields.CharField(max_length=30, unique=True)
    series = fields.ForeignKeyField('models.Series', related_name='seasons')
    cars: fields.ManyToManyRelation["Car"] = fields.ManyToManyField(
        "models.Car", related_name="seasons", through="season_cars"
    )
    minimum_team_drivers = fields.IntField(default=1)
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    season_quarter = fields.IntField(null=True)
    season_year = fields.IntField(null=True)
    is_fixed = fields.BooleanField(null=True)
    is_official = fields.BooleanField(null=True)
    active = fields.BooleanField(null=True)

    def current_week(self):
        current_datetime = datetime.now()
        utc_time = current_datetime.replace(tzinfo=timezone.utc)
        return (utc_time - self.start_time).days // 7

    async def current_combo(self):
        return await SeasonCombo.get(
            season=self,
            race_week=self.current_week()
        )

    async def offset_combo(self, offset):
        """offset is how far off the current week we want a combo for.
            so 1 would be 1 week after current, -1 would be the week before current"""
        try:
            return await SeasonCombo.get(
                season=self,
                race_week=(self.current_week() + offset)
            )
        except:
            return None


class Car(Base):
    iracing_id = fields.CharField(max_length=30)
    seasons: fields.ManyToManyRelation[Season]
    name = fields.TextField()
    sku = fields.TextField(null=True)


class SeasonCombo(Base):
    season = fields.ForeignKeyField('models.Season', related_name='season_combos')
    track = fields.ForeignKeyField('models.Track', related_name='season_combos')
    race_week = fields.IntField()
    track_layout = fields.TextField(null=True)
    time_of_day = fields.IntField(null=True)


class Stat(Base):
    driver = fields.ForeignKeyField('models.Driver', related_name='stats')
    category: Category = fields.IntEnumField(Category)
    stat_type: StatsType = fields.IntEnumField(StatsType)
    avg_incidents = fields.TextField(null=True)
    total_laps = fields.IntField(null=True)
    laps_led = fields.IntField(null=True)
    laps_led_percentage = fields.TextField(null=True)
    points_avg = fields.IntField(null=True)
    points_club = fields.IntField(null=True)
    poles = fields.IntField(null=True)
    avg_start_pos = fields.IntField(null=True)
    avg_finish_pos = fields.IntField(null=True)
    total_starts = fields.IntField(null=True)
    top_five_percentage = fields.IntField(null=True)
    total_top_fives = fields.IntField(null=True)
    win_percentage = fields.IntField(null=True)
    total_wins = fields.IntField(null=True)
    year = fields.TextField(null=True)


class League(Base):
    iracing_id = fields.CharField(max_length=30)
    name = fields.TextField()
    seasons: fields.ReverseRelation["LeagueSeason"]
    guilds: fields.ManyToManyRelation[Guild] = fields.ManyToManyField(
        "models.Guild", related_name="leagues", through="guild_leagues"
    )


class LeagueSeason(Base):
    league = fields.ForeignKeyField('models.League', related_name='seasons')
    iracing_id = fields.CharField(max_length=30)
    name = fields.TextField()
    active = fields.IntField()
    league_points_system_description = fields.TextField(null=True)
    league_points_system_name = fields.TextField(null=True)
    league_points_system_id = fields.CharField(max_length=30, null=True)
