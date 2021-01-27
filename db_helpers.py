from .models import Series, Season, SeasonCombo, Car, Track


async def get_or_create_series(series):
    series_model = await Series.get_or_create(
        iracing_id=series.series_id,
        defaults={
            'name': series.series_name_short,
            'category_id': series.cat_id
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
        defaults={
            'track': track_model,
            'track_layout': track.config,
            'race_week': track.race_week,
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
