from tortoise import Tortoise, run_async
from models import Guild, Driver, Irating


async def init_tortoise():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas(safe=True)

    # guild = await Guild.create(discord_id='172938472984')
    # driver = await Driver.create(discord_id='12398729847')
    # await driver.guilds.add(guild)
    #
    # print(guild.discord_id)
    # async for driver1 in guild.drivers:
    #     print(driver1.discord_id)
    # print(driver.discord_id)


if __name__ == "__main__":
    run_async(init_tortoise())
