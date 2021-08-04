import discord

from database import DBManager
from utils.message_embed import CreateEmbed
from const import MESSAGE_LIMIT, PREFIX

class GuildAnalysis:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.receive_guild = None
        self.target_guild = None

    def user_perm(self, channel):
        member_perm = []
        access_perm = []
        
        for role, perm in channel.overwrites.items():
            if isinstance(role, discord.member.Member):
                for access in perm.pair():
                    access_perm.append(str(access.value))
                member_perm.append(f"{role.id}:{','.join(access_perm)}")
            access_perm.clear()
        
        return ';'.join(member_perm)

    async def change_permissions(self, channel, roles) -> dict:
        permissions = {}

        for role, perm in channel.overwrites.items():
            if isinstance(role, discord.member.Member):
                if role in self.receive_guild.members:
                    permissions[role] = perm
                else:
                    continue
            else:
                permissions[roles.get(role.id)] = perm

        return permissions

    async def category_creation(self, category, roles) -> discord.CategoryChannel:

        options = {
            "name": category.name,
            "overwrites": await self.change_permissions(category, roles),
            "reason": "Bot deepcopy"
        }
        
        return await self.receive_guild.create_category(**options)

    async def role_creation(self, role) -> discord.Role:
        options = {
            "name": role.name,
            "permissions": role.permissions,
            "colour": role.colour,
            "hoist": role.hoist,
            "mentionable": role.mentionable,
            "reason": "Bot deepcopy"
        }

        return await self.receive_guild.create_role(**options)

    async def role_edit(self, role) -> discord.Role:
        options = {
            "name": role.name,
            "permissions": role.permissions,
            "colour": role.colour,
            "hoist": role.hoist,
            "mentionable": role.mentionable,
            "reason": "Bot deepcopy"
        }

        await self.receive_guild.default_role.edit(**options)

    async def textchannel_creation(self, channel, roles, categories) -> discord.TextChannel:

        options = {
            "name": channel.name,
            "overwrites": await self.change_permissions(channel, roles),
            "category": categories.get(channel.category_id),
            "topic": channel.topic,
            "slowmode_delay": channel.slowmode_delay,
            "nsfw": channel.is_nsfw(),
            "reason": "Bot deepcopy"
        }

        return await self.receive_guild.create_text_channel(**options)

    async def voicechannel_creation(self, channel, roles, categories):
        
        options = {
            "name": channel.name,
            "overwrites": await self.change_permissions(channel, roles),
            "category": categories.get(channel.category_id),
            "bitrate": channel.bitrate,
            "rtc_region": channel.rtc_region,
            "user_limit": channel.user_limit,
            "reason": "Bot deepcopy"
        }

        return await self.receive_guild.create_voice_channel(**options)

    async def emoji_creation(self, emoji, roles):

        options = {
            "name": emoji.name,
            "image": await emoji.url.read(),
            "roles": [roles.get(r.id) for r in emoji.roles],
            "reason": "Bot deepcopy"
        }

        await self.receive_guild.create_custom_emoji(**options)


    async def role_analyse(self) -> dict:
        roles = {self.target_guild.default_role.id: self.receive_guild.default_role}
        for role in self.target_guild.roles[::-1]:
            if role.id != self.target_guild.default_role.id:
                roles[role.id] = await self.role_creation(role)
            else:
                await self.role_edit(role)

        return roles

    async def category_analyse(self, roles) -> dict:
        categories = {}
        for category in self.target_guild.categories:
            new_category = await self.category_creation(category, roles)
            categories[category.id] = new_category
            DBManager().add_channel(new_category, self.receive_guild, self.user_perm(category))

        return categories

    async def text_analyse(self, roles, categories):
        textchannels = {}
        for text in self.target_guild.text_channels:
            new_text = await self.textchannel_creation(text, roles, categories)
            textchannels[text.id] = new_text
            DBManager().add_channel(new_text, self.receive_guild, self.user_perm(text))

        return textchannels

    async def voice_analyse(self, roles, categories):
        voicechannels = {}
        for voice in self.target_guild.voice_channels:
            new_voice = await self.voicechannel_creation(voice, roles, categories)
            voicechannels[voice.id] = new_voice
            DBManager().add_channel(new_voice, self.receive_guild, self.user_perm(voice))

        return voicechannels

    async def emoji_analyse(self, roles):
        for emoji in self.target_guild.emojis:
            await self.emoji_creation(emoji, roles)

    async def member_analyse(self, roles, owner):
        for member in self.target_guild.members:
            role_id = [r.id for r in member.roles]

            member_role = ';'.join(str(p.id) for i, p in roles.items() if i in role_id)
            DBManager().add_member(member, self.receive_guild, member_role, owner)

    async def sync_ban(self):
        ban_user = await self.target_guild.bans()
        for entry in ban_user:
            await self.receive_guild.ban(entry.user, reason=entry.reason)

    async def sync_guild(self, voicechannels, textchannels, categories):
        guild = self.target_guild
        features = guild.features

        afk_channel = None
        if guild.afk_channel:
            afk_channel = guild.afk_channel.id

        system_channel = None
        if guild.system_channel:
            system_channel = guild.system_channel.id


        options = {
            "description": guild.description,
            "afk_channel": voicechannels.get(afk_channel),
            "afk_timeout": guild.afk_timeout,
            "verification_level": guild.verification_level,
            "default_notifications": guild.default_notifications,
            "explicit_content_filter": guild.explicit_content_filter,
            "system_channel": textchannels.get(system_channel),
            "system_channel_flags": guild.system_channel_flags,
            "name": guild.name,
            "region": guild.region,
            "icon": await guild.icon_url.read() if "ANIMATED_ICON" in features else await guild.icon_url_as(static_format="webp").read(),
            "reason": "Bot deepcopy"
        }
        
        await self.receive_guild.edit(**options)
        channels = list(voicechannels.values()) + list(textchannels.values()) + list(categories.values())
        channels_id = ';'.join(str(i.id) for i in channels)
        DBManager().edit_guild(self.receive_guild, channels_id)

    async def sync_message(self, textchannels):
        for channel in self.target_guild.text_channels:
            messages = await channel.history(limit=MESSAGE_LIMIT).flatten()
            messages.reverse()
            print(f"Writing {channel} messages...")
            counter = 0
            for message in messages:
                counter += 1
                channel_id = message.channel.id
                send_channel = textchannels.get(channel_id)
                await CreateEmbed().send_message(send_channel, message)

                if counter % 150 == 0:
                    print(f"Still writing messages in {channel}.")

        

    async def start_analyse(self, receive_guild, target_guild, ctx):
        features = target_guild.features
        print("Creating a guild.")
        receive_guild = await self.bot.create_guild(
            name=target_guild.name,
            region=target_guild.region,
            icon=await target_guild.icon_url.read() if "ANIMATED_ICON" in features else await target_guild.icon_url_as(static_format="webp").read()
        )
        print(f"If something goes wrong, please type: {PREFIX}delete {receive_guild.id}")

        await ctx.send("Creating the guild, please wait until the bot send you an invite link.\nPlease check your console in case an error occured during the process.\nIt will take a while, please wait...")
        await ctx.send(F"If something goes wrong, please type: {PREFIX}delete {receive_guild.id}\nIf the process takes too much time, please set a limit in the file const.py after the variable MESSAGE_LIMIT (default: None : there is no limit) (eg: MESSAGE_LIMIT = 2000).")

        self.target_guild = target_guild
        self.receive_guild = receive_guild
        DBManager().add_guild(self.receive_guild)
        print("Creating roles.")
        roles = await self.role_analyse()
        print("Adding members to the database")
        await self.member_analyse(roles, ctx.author)
        print("Creating categories channels.")
        categories = await self.category_analyse(roles)
        print("Creating text channels.")
        textchannels = await self.text_analyse(roles, categories)
        print("Creating voice channels.")
        voicechannels = await self.voice_analyse(roles, categories)
        print("Creating emojis.")
        await self.emoji_analyse(roles)
        print("Adding ban members.")
        await self.sync_ban()
        print("Editing guild configurations.")
        await self.sync_guild(voicechannels, textchannels, categories)
        print("Writing the messages.")
        await self.sync_message(textchannels)
        print("Creating an invite")
        invite = await self.receive_guild.text_channels[0].create_invite(reason="Bot deepcopy")
        await ctx.author.send(invite)
        print("Done!")
        await ctx.send("All is done! Please enter the guild.")
        await ctx.send(f"If the bot don't grant you the guild ownership, please write {PREFIX}admin {ctx.author.id}.")
        await ctx.send(f"If the bot don't automaticly give roles to newcoming members, please write {PREFIX}debug <member.id or member mention> (without the <>).")


# TODO integrations
# TODO stage channel