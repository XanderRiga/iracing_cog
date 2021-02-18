from ..db_helpers import init_tortoise
from datetime import datetime


async def get_irating_dicts(guild, category):
    irating_dicts = []
    async for driver in guild.drivers:

        irating_list = await driver.iratings.filter(category=category)
        current_irating = await get_current_irating_now(driver, category)
        irating_list.append(current_irating)
        irating_dicts.append({driver.discord_id: irating_list})

    return irating_dicts


async def get_current_irating_now(driver, category):

    current_irating = await driver.current_irating(category)
    current_irating.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return current_irating
