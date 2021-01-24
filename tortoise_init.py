from tortoise import Tortoise, run_async
from models import Driver, Irating


async def init_tortoise():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas(safe=True)


if __name__ == "__main__":
    run_async(init_tortoise())
