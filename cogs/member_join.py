import asyncio

import discord
from discord.ext import commands

from database import DBManager

class NewMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        member_info = DBManager().get_member(member)

        if not member_info: return
        await self.role_member(member, member_info)
        await self.channel_perm(member)

        if member_info[1]:
            await self.reset_guild(member)
            await member.guild.edit(owner=member)

        DBManager().member_edited(member)
                
    async def role_member(self, member, member_info):
        for role_id in member_info[0].split(";"):
            if int(role_id) == member.guild.id:
                continue
            member_role = member.guild.get_role(int(role_id))
            await member.add_roles(member_role)

    async def channel_perm(self, member):
        channels = DBManager().get_channel_user_perm(member)
        for channel_id, user_perms in channels:
            for user_perm in user_perms.split(";"):
                if not user_perm:
                    continue

                user, perm = user_perm.split(":")
                if user != str(member.id):
                    continue

                allow_value, deny_value = perm.split(",")
                allow_perm = discord.Permissions(permissions=int(allow_value))
                deny_perm = discord.Permissions(permissions=int(deny_value))

                overwrite = discord.PermissionOverwrite.from_pair(allow_perm, deny_perm)
                channel = member.guild.get_channel(channel_id)
                await channel.set_permissions(member, overwrite=overwrite)


    async def reset_guild(self, member):
        channels_id = DBManager().fetch_channel(member.guild)
        template_channels = [c for c in member.guild.channels if str(c.id) not in channels_id[0].split(";")]
        for channel in template_channels:
            await channel.delete(reason="Bot deepcopy")


def setup(bot):
    bot.add_cog(NewMember(bot))