import discord
from discord.ext import commands

from utils.analysis import GuildAnalysis
from utils.message_embed import CreateEmbed


class DeepCopy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Command
    async def copy(self, ctx, target: discord.Guild):
        receive_guild = ctx.guild
        await GuildAnalysis(self.bot).start_analyse(receive_guild, target, ctx.author)

    @commands.Command
    async def admin(self, ctx):
        await ctx.guild.edit(owner=ctx.author)

    @commands.Command
    async def delete(self, ctx, guild: discord.Guild):
        await guild.delete()
        print("Guild deleted")

    @commands.Command
    async def debug(self, ctx, message: discord.Message):
        await CreateEmbed().send_message(ctx.channel, message)


def setup(client):
    client.add_cog(DeepCopy(client))