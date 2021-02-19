from ..db_helpers import *


class SaveId:
    def __init__(self, log):
        self.log = log

    async def call(self, ctx, iracing_id):
        if not iracing_id.isdigit():
            await ctx.send('Oops, this ID does not seem to be valid. '
                           + 'Make sure you only write the numbers and not any symbols with the ID.'
                           + 'Your ID can be found by the top right of your account page under "Customer ID".')
            self.log.info(f'Failed to save iracing id: {iracing_id}')
            return

        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        await create_or_update_driver(iracing_id, user_id, guild_id)
        await ctx.send('iRacing ID successfully saved. Use `!update` to see this user on the leaderboard.')
