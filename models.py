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
    # guilds = fields.ManyToManyField('models.Guild', related_name='drivers')
    iracing_name = fields.CharField(max_length=30, null=True)
    iracing_id = fields.CharField(max_length=30, null=True)

    def __str__(self):
        return self.name


class Guild(Base):
    discord_id = fields.CharField(max_length=30, unique=True)
    drivers: fields.ManyToManyRelation[Driver]

