from tortoise import fields, Tortoise
from tortoise.models import Model
from enum import IntEnum


class Category(IntEnum):
    oval = 1
    road = 2
    dirt_road = 3
    dirt_oval = 4


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
    discord_id = fields.CharField(max_length=30, unique=True)
    guilds: fields.ManyToManyRelation["Guild"] = fields.ManyToManyField(
        "models.Guild", related_name="drivers", through="driver_guild"
    )
    iracing_name = fields.CharField(max_length=30, null=True)
    iracing_id = fields.CharField(max_length=30, null=True)

    def __str__(self):
        return self.name


class Guild(Base):
    discord_id = fields.CharField(max_length=30, unique=True)
    drivers: fields.ManyToManyRelation[Driver]


class Track(Base):
    iracing_id = fields.CharField(max_length=30)
    name = fields.CharField(max_length=100)


class Car(Base):
    iracing_id = fields.CharField(max_length=30)
    name = fields.CharField(max_length=100)
    sku = fields.CharField(max_length=30, null=True)


class Series(Base):
    iracing_id = fields.CharField(max_length=30, unique=True)
    name = fields.CharField(max_length=100)
    category_id = fields.IntField()


class Season(Base):
    season_combos: fields.ReverseRelation["SeasonCombo"]
    iracing_id = fields.CharField(max_length=30, unique=True)
    series = fields.ForeignKeyField('models.Series', related_name='seasons')
    is_official = fields.BooleanField()
    active = fields.BooleanField()
    minimum_team_drivers = fields.IntField()
    start_time = fields.CharField(max_length=30)
    end_time = fields.CharField(max_length=30)
    current_race_week = fields.IntField()

    # TODO use the start date and the current date difference
    #  to determine what the current race week is and find the combo from that
    def current_combo(self):
        return None


class SeasonCombo(Base):
    season = fields.ForeignKeyField('models.Season', related_name='season_combos')
    track = fields.ForeignKeyField('models.Track', related_name='season_combos')
    cars: fields.ManyToManyRelation["Car"] = fields.ManyToManyField(
        "models.Car", related_name="season_combos", through="season_combo_cars"
    )
    iracing_id = fields.CharField(max_length=30)
    race_week = fields.IntField()
    time_of_day = fields.IntField()
