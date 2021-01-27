from .models import Series


async def get_or_create_series(series, log):
    try:
        series_model = await Series.get(iracing_id=series.series_id)
        await series_model.update_from_dict({
            'name': series.series_name_short,
            'category_id': series.cat_id
        })
        return series_model
    except Exception as e:
        log.info(f'Creating series {series.series_name_short}')
        return await Series.create(
            iracing_id=series.series_id,
            name=series.series_name_short,
            category_id=series.cat_id
        )
