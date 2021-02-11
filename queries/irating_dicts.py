from ..db_helpers import init_tortoise


async def get_irating_dicts(guild, category):
    irating_dicts = []
    async for driver in guild.drivers:
        await init_tortoise()
        irating_list = await driver.iratings.filter(category=category)
        irating_dicts.append({driver.discord_id: irating_list})

    return irating_dicts
