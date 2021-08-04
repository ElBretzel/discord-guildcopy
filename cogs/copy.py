import discord
from discord.ext import commands

from database import DBManager

from cogs.member_join import role_member, channel_perm, reset_guild
from utils.analysis import GuildAnalysis


class DeepCopy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Command
    @commands.has_guild_permissions(administrator=True)
    async def copy(self, ctx, target: discord.Guild):
        receive_guild = ctx.guild
        await GuildAnalysis(self.bot).start_analyse(receive_guild, target, ctx)

    @commands.Command
    @commands.has_guild_permissions(administrator=True)
    async def admin(self, ctx):
        await ctx.guild.edit(owner=ctx.author)

    @commands.Command
    @commands.has_guild_permissions(administrator=True)
    async def delete(self, ctx, guild: discord.Guild):
        await guild.delete()
        print("Guild deleted")

    @commands.Command
    @commands.has_guild_permissions(administrator=True)
    async def debug(self, ctx, member: discord.Member):
        member_info = DBManager().get_member(member)

        if not member_info: return
        await role_member(member, member_info)
        await channel_perm(member)

        if member_info[1]:
            await reset_guild(member, self.bot)
            await member.guild.edit(owner=member)

        DBManager().member_edited(member)
        

def setup(client):
    client.add_cog(DeepCopy(client))