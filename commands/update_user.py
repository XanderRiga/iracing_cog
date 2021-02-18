import asyncio
from pyracing.constants import Category
from ..helpers import *
from ..errors.name_not_found import NameNotFound
from ..db_helpers import *
from tortoise import Tortoise
import traceback


class UpdateUser:
    def __init__(self, pyracing, log):
        self.pyracing = pyracing
        self.log = log

    async def update_fields(self, driver):
        """This updates a user inside the dict without saving to any files"""

        try:
            await self.update_driver_name(driver)
        except Exception as e:
            self.handle_exceptions(self.update_driver_name.__name__, e)

        try:
            await self.update_career_stats(driver)
        except Exception as e:
            self.handle_exceptions(self.update_career_stats.__name__, e)

        try:
            await self.update_yearly_stats(driver)
        except Exception as e:
            self.handle_exceptions(self.update_yearly_stats.__name__, e)

        try:
            await self.update_iratings(driver, Category.oval)
        except Exception as e:
            self.handle_exceptions(self.update_iratings.__name__, e)

        try:
            await self.update_iratings(driver, Category.road)
        except Exception as e:
            self.handle_exceptions(self.update_iratings.__name__, e)

        try:
            await self.update_iratings(driver, Category.dirt_road)
        except Exception as e:
            self.handle_exceptions(self.update_iratings.__name__, e)

        try:
            await self.update_iratings(driver, Category.dirt_oval)
        except Exception as e:
            self.handle_exceptions(self.update_iratings.__name__, e)

        try:
            await self.update_license_class(driver, Category.oval)
        except Exception as e:
            self.handle_exceptions(self.update_license_class.__name__, e)

        try:
            await self.update_license_class(driver, Category.road)
        except Exception as e:
            self.handle_exceptions(self.update_license_class.__name__, e)

        try:
            await self.update_license_class(driver, Category.dirt_road)
        except Exception as e:
            self.handle_exceptions(self.update_license_class.__name__, e)

        try:
            await self.update_license_class(driver, Category.dirt_oval)
        except Exception as e:
            self.handle_exceptions(self.update_license_class.__name__, e)

    async def update_driver_name(self, driver):
        try:
            response = await self.pyracing.driver_status(cust_id=driver.iracing_id)
            name = parse_encoded_string(response.name)

            driver.update_from_dict({'iracing_name': name})
            await driver.save()
            return name
        except:
            self.log.warning(f'Name not found for {driver}')

    async def update_career_stats(self, driver):
        career_stats_list = await self.pyracing.career_stats(driver.iracing_id)
        if career_stats_list:
            try:
                for stat in career_stats_list:
                    await create_or_update_stat_from_driver(driver, stat, StatsType.career)
                return career_stats_list
            except:
                self.log.info('skipping saving for career stats')
                return career_stats_list
        else:
            return []

    async def update_yearly_stats(self, driver):
        yearly_stats_list = await self.pyracing.yearly_stats(driver.iracing_id)
        if yearly_stats_list:
            try:
                for stat in yearly_stats_list:
                    await create_or_update_stat_from_driver(driver, stat, StatsType.yearly)
                return yearly_stats_list
            except:
                self.log.info('skipping saving for yearly stats')
                return yearly_stats_list
        else:
            return []

    async def update_iratings(self, driver, category):
        chart_data = await self.pyracing.irating(driver.iracing_id, category.value)
        if not chart_data.current():
            return []

        for irating in chart_data.content:
            await get_or_create_irating_for_driver(driver, irating, category)

        return chart_data

    async def update_license_class(self, driver, category):
        chart_data = await self.pyracing.license_class(driver.iracing_id, category.value)
        if not chart_data.current():
            return 'N/A'

        await get_or_create_license_for_driver(driver, chart_data.current(), category)

    def handle_exceptions(self, method_name, e):
        traceback.print_exc()
        self.log.warning(f'update failed in method {method_name}. Exception: {str(e)}')
