from tortoise import fields
from tortoise.models import Model
from enum import IntEnum


class Category(IntEnum):
    oval = 1
    road = 2
    dirt_road = 3
    dirt_oval = 4


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

    def __str__(self):
        return f'{self.driver.discord_id} irating for {self.category} at {self.timestamp}'


class Driver(Base):
    iratings: fields.ReverseRelation["Irating"]
    stats: fields.ReverseRelation["Stat"]
    discord_id = fields.CharField(max_length=30, unique=True)
    guilds: fields.ManyToManyRelation["Guild"] = fields.ManyToManyField(
        "models.Guild", related_name="drivers", through="driver_guild"
    )
    iracing_name = fields.TextField()
    iracing_id = fields.TextField()

    def __str__(self):
        return self.iracing_name


class Guild(Base):
    discord_id = fields.CharField(max_length=30, unique=True)
    favorite_series: fields.ManyToManyRelation["Series"] = fields.ManyToManyField(
        "models.Series", related_name="guilds", through="favorite_series"
    )
    drivers: fields.ManyToManyRelation[Driver]


class Track(Base):
    iracing_id = fields.CharField(max_length=30)
    name = fields.TextField()


class Series(Base):
    iracing_id = fields.CharField(max_length=30, unique=True)
    favorited_guilds: fields.ManyToManyRelation[Guild]
    name = fields.TextField()
    category_id = fields.IntField()


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

    # TODO use the start date and the current date difference
    #  to determine what the current race week is and find the combo from that
    def current_combo(self):
        return None


class Car(Base):
    iracing_id = fields.CharField(max_length=30)
    seasons: fields.ManyToManyRelation[Season]
    name = fields.TextField()
    sku = fields.TextField(null=True)


class SeasonCombo(Base):
    season = fields.ForeignKeyField('models.Season', related_name='season_combos')
    track = fields.ForeignKeyField('models.Track', related_name='season_combos')
    track_layout = fields.TextField()
    race_week = fields.IntField()
    time_of_day = fields.IntField(null=True)


class Stat(Base):
    driver = fields.ForeignKeyField('models.Driver', related_name='stats')
    category: Category = fields.IntEnumField(Category)
    stats_type: StatsType = fields.IntEnumField(StatsType)
    avg_incidents = fields.TextField()
    total_laps = fields.IntField()
    laps_led = fields.IntField()
    laps_led_percentage = fields.TextField()
    points_avg = fields.IntField()
    points_club = fields.IntField()
    poles = fields.IntField()
    avg_start_pos = fields.IntField()
    avg_finish_pos = fields.IntField()
    total_starts = fields.IntField()
    top_five_percentage = fields.IntField()
    total_top_fives = fields.IntField()
    win_percentage = fields.IntField()
    total_wins = fields.IntField()
    year = fields.TextField(null=True)
