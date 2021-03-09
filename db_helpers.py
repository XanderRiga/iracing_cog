from .models import *
from tortoise import Tortoise
from datetime import datetime
import traceback

TORTOISE_ORM = {
    "connections": {"default": 'sqlite://db.sqlite3'},
    "apps": {
        "models": {
            'models': ['iracing_cog.models', 'aerich.models'],
            "default_connection": "default",
        },
    },
}


async def init_tortoise():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['iracing_cog.models', 'aerich.models']}
    )


async def generate_schemas():
    await init_tortoise()
    await Tortoise.generate_schemas(safe=True)


async def get_or_create_series(series):
    series_model = await Series.get_or_create(
        iracing_id=series.series_id,
        defaults={
            'name': series.series_name_short,
            'category': Category(series.cat_id)
        }
    )

    return series_model[0]


async def get_or_create_season(series):
    series_model = await Series.get(iracing_id=series.series_id)
    cars = [await get_or_create_car(x) for x in series.cars]

    season_model = await Season.get_or_create(
        iracing_id=series.season_id,
        defaults={
            'series': series_model,
            'start_time': series.date_start,
            'end_time': series.date_end,
            'active': series.active,
            'season_quarter': series.season_quarter,
            'season_year': series.season_year
        }
    )

    for car in cars:
        await season_model[0].cars.add(car)

    for track in series.tracks:
        await get_or_create_season_combo(track, season_model[0])

    return season_model[0]


async def get_or_create_season_combo(track, season):
    track_model = await get_or_create_track(track)
    season_combo = await SeasonCombo.get_or_create(
        season=season,
        race_week=track.race_week,
        defaults={
            'track': track_model,
            'track_layout': track.config,
            'time_of_day': track.time_of_day
        }
    )
    return season_combo[0]


async def get_or_create_track(track):
    track_model = await Track.get_or_create(
        iracing_id=track.id,
        defaults={'name': track.name}
    )

    return track_model[0]


async def get_or_create_car(car):
    car_model = await Car.get_or_create(
        iracing_id=car.id,
        defaults={
            'name': car.name,
            'sku': car.sku
        }
    )

    return car_model[0]


async def get_or_create_driver(discord_id, guild_id, iracing_id, name=None):
    guild_model = await get_or_create_guild(guild_id)
    driver_model = await Driver.get_or_create(
        discord_id=discord_id,
        defaults={'iracing_id': iracing_id}
    )

    driver = driver_model[0]
    if name:
        driver.iracing_name = name
        await driver.save()

    await driver.guilds.add(guild_model)
    return driver


# This also deletes all previous data from this driver
async def create_or_update_driver(iracing_id, discord_id, guild_id, name=None):
    guild_model = await get_or_create_guild(guild_id)
    driver = await Driver.get_or_none(discord_id=discord_id)

    if driver:
        await driver.update_from_dict({'iracing_name': name, 'iracing_id': iracing_id})
        await driver.save()
    else:
        driver = await Driver.create(
            discord_id=discord_id,
            iracing_name=name,
            iracing_id=iracing_id
        )

    driver = await get_or_create_driver(discord_id, guild_id, iracing_id, name)
    await driver.guilds.add(guild_model)
    await remove_driver_data(driver)
    return driver


async def remove_driver_data(driver):
    try:
        await Irating.filter(driver=driver).delete()
    except:
        pass
    try:
        await License.filter(driver=driver).delete()
    except:
        pass
    try:
        await Stat.filter(driver=driver).delete()
    except:
        pass


async def create_or_update_stat_from_driver(driver, stat, stat_type):
    if stat_type == StatsType.career:
        stat_model_tuple = await Stat.get_or_create(
            driver=driver,
            category=Category.from_name(stat.category),
            stat_type=StatsType.career
        )

        stat_model = stat_model_tuple[0]
    else:
        stat_model_tuple = await Stat.get_or_create(
            driver=driver,
            category=Category.from_name(stat.category),
            stat_type=StatsType.yearly,
            year=stat.year
        )

        stat_model = stat_model_tuple[0]

    await stat_model.update_from_dict({
        'avg_incidents': stat.incidents_avg,
        'total_laps': stat.laps,
        'laps_led': stat.laps_led,
        'laps_led_percentage': stat.laps_led_pcnt,
        'points_avg': stat.points_avg,
        'points_club': stat.points_club,
        'poles': stat.poles,
        'avg_start_pos': stat.pos_start_avg,
        'avg_finish_pos': stat.pos_finish_avg,
        'total_starts': stat.starts,
        'top_five_percentage': stat.top_5_pcnt,
        'total_top_fives': stat.top_5s,
        'win_percentage': stat.win_pcnt,
        'total_wins': stat.wins,
    })

    await stat_model.save()
    return stat_model


async def create_or_update_stats(driver_discord_id, guild_id, stat, stat_type, driver_iracing_id):
    driver_model = await get_or_create_driver(driver_discord_id, guild_id, driver_iracing_id)
    if stat_type == StatsType.career:
        stat_model_tuple = await Stat.get_or_create(
            driver=driver_model,
            category=Category.from_name(stat.category),
            stat_type=StatsType.career
        )
        stat_model = stat_model_tuple[0]
    else:
        stat_model_tuple = await Stat.get_or_create(
            driver=driver_model,
            category=Category.from_name(stat.category),
            stat_type=StatsType.yearly,
            year=stat.year
        )
        stat_model = stat_model_tuple[0]

    await stat_model.update_from_dict({
        'avg_incidents': stat.incidents_avg,
        'total_laps': stat.laps,
        'laps_led': stat.laps_led,
        'laps_led_percentage': stat.laps_led_pcnt,
        'points_avg': stat.points_avg,
        'points_club': stat.points_club,
        'poles': stat.poles,
        'avg_start_pos': stat.pos_start_avg,
        'avg_finish_pos': stat.pos_finish_avg,
        'total_starts': stat.starts,
        'top_five_percentage': stat.top_5_pcnt,
        'total_top_fives': stat.top_5s,
        'win_percentage': stat.win_pcnt,
        'total_wins': stat.wins,
    })

    await stat_model.save()
    return stat_model


async def get_or_create_guild(guild_id):
    guild_model = await Guild.get_or_create(
        discord_id=guild_id
    )

    return guild_model[0]


async def update_driver_name(discord_id, guild_id, name, iracing_id):
    guild_model = await get_or_create_guild(guild_id)
    driver_model = await get_or_create_driver(discord_id, guild_id, iracing_id)
    driver_model.iracing_name = name

    await driver_model.save()
    await driver_model.guilds.add(guild_model)
    return driver_model


async def get_or_create_irating_for_driver(driver, irating, category):
    irating_timestamp = datetime.fromtimestamp((irating.timestamp / 1000))
    irating_model = await Irating.get_or_create(
        timestamp=irating_timestamp,
        driver=driver,
        category=Category(category),
        defaults={
            'value': irating.value
        }
    )

    return irating_model[0]


async def get_or_create_irating(guild_id, driver_discord_id, irating, category, driver_iracing_id):
    driver_model = await get_or_create_driver(driver_discord_id, guild_id, driver_iracing_id)
    irating_timestamp = datetime.fromtimestamp((irating.timestamp / 1000))

    irating_model = await Irating.get_or_create(
        timestamp=irating_timestamp,
        driver=driver_model,
        category=Category(category),
        defaults={
            'value': irating.value
        }
    )

    return irating_model[0]


async def get_or_create_license_for_driver(driver, license_class, category):
    license_timestamp = datetime.fromtimestamp((license_class.timestamp / 1000))
    license_model = await License.get_or_create(
        timestamp=license_timestamp,
        driver=driver,
        category=Category(category),
        defaults={
            'license_number': license_class.license_number
        }
    )

    return license_model[0]


async def get_or_create_license(guild_id, driver_discord_id, license_class, category, driver_iracing_id):
    driver_model = await get_or_create_driver(driver_discord_id, guild_id, driver_iracing_id)
    license_timestamp = datetime.fromtimestamp((license_class.timestamp / 1000))

    license_model = await License.get_or_create(
        timestamp=license_timestamp,
        driver=driver_model,
        category=Category(category),
        defaults={
            'license_number': license_class.license_number
        }
    )

    return license_model[0]


async def set_all_fav_series(guild_id, series_ids):
    for series_id in series_ids:
        await add_fav_series(guild_id, series_id)


async def add_fav_series(guild_id, series_id):
    guild = await get_or_create_guild(guild_id)
    series = await Series.get(iracing_id=series_id)
    await guild.favorite_series.add(series)


async def remove_fav_series(guild_id, series_id):
    guild = await get_or_create_guild(guild_id)
    series = await Series.get(iracing_id=series_id)
    await guild.favorite_series.remove(series)


async def remove_league(guild_id, league_id):
    guild = await get_or_create_guild(guild_id)
    league = await League.get(iracing_id=league_id)
    await guild.leagues.remove(league)
