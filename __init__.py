from .iracing import Iracing


def setup(bot):
    bot.add_cog(Iracing())
