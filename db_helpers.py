from .models import Series


async def get_or_create_series(series):
    try:
        print(f'getting series for {series}')
        series_model = await Series.get(iracing_id=series.series_id)
        await series_model.update_from_dict({
            'name': series.series_name_short,
            'category_id': series.cat_id
        })
        return series_model
    except Exception:
        return await Series.create(
            iracing_id=series.series_id,
            name=series.series_name_short,
            category_id=series.cat_id
        )
