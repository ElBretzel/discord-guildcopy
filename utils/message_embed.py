from os import name
from discord import Embed, Colour
from discord import HTTPException, InvalidArgument
import discord

from const import TIMEZONE

class CreateEmbed:
    def __init__(self) -> None:
        self.message = None

    def footer(self, embed: Embed):
        if self.message.edited_at:
            embed.set_footer(text="Message édité.", icon_url="https://www.emoji.co.uk/files/mozilla-emojis/symbols-mozilla/12051-heavy-exclamation-mark-symbol.png")

    @property
    def content(self):
        content = []
        if self.message.content:
            content.append(self.message.clean_content)
        if self.message.attachments:
            content.append("**[Un ou plusieurs fichiers sont liés au message]**")

        return '\n'.join(content)

    @property
    def embed_template(self):

        embed = Embed(
                    title=f"Créé le {self.message.created_at.astimezone(TIMEZONE).strftime('%d/%m/%Y')}",
                    description=f"{self.content}",
                    colour=Colour.blurple())
        embed.set_author(name=self.message.author, icon_url=self.message.author.avatar_url)
        embed.add_field(name="\u200b", value=f"[Message]({self.message.jump_url}) envoyé par :")
        embed.add_field(name="\u200b", value=self.message.author.mention)
        self.footer(embed)

        return embed

    async def check_pin(self, message_sent):
        if self.message.pinned:
            await message_sent.pin(reason="Bot deepcopy")

    async def send_message(self, channel, message: discord.Message):

        self.message = message
        files = []
        for at in self.message.attachments:
            file = await at.to_file(spoiler=at.is_spoiler())
            files.append(file)

        embed = self.embed_template

        try:
            message_sent = await channel.send(embed=embed, files=files)
            await self.check_pin(message_sent)
        except (HTTPException, InvalidArgument) as e:
            print(e)




# pinn