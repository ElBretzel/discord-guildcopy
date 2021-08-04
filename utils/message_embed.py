from pprint import pprint

from discord import Embed, Colour
from discord import HTTPException, InvalidArgument

from const import *


class CreateEmbed:
    def __init__(self) -> None:
        self.message = None

    def footer(self, embed: Embed):
        if self.message.edited_at:
            embed.set_footer(text=MAIN_LANGUAGE["embed_footer_edited"], icon_url=ICON_URL)

    @property
    def content(self):
        content = []
        if self.message.content:
            content.append(self.message.clean_content)
        if self.message.attachments:
            content.append(f"**[{MAIN_LANGUAGE['embed_description_files']}]**")

        return '\n'.join(content)

    @property
    def embed_template(self):

        # Time format: 
        # %d : day
        # %m : month
        # %Y : year (all digit)
        # See more : https://docs.python.org/fr/3/library/datetime.html#strftime-and-strptime-format-codes

        embed = Embed(
                    title=f"{MAIN_LANGUAGE['embed_title_created']} {self.message.created_at.astimezone(TIMEZONE).strftime('%d/%m/%Y')}", # You can edit format here
                    description=f"{self.content}",
                    colour=Colour.blurple())
        embed.set_author(name=self.message.author, icon_url=self.message.author.avatar_url)
        embed.add_field(name="\u200b", value=f"[{MAIN_LANGUAGE['embed_field_message']}]({self.message.jump_url}) {MAIN_LANGUAGE['embed_field_sent']}")
        embed.add_field(name="\u200b", value=self.message.author.mention)
        self.footer(embed)

        return embed

    async def check_pin(self, message_sent):
        if self.message.pinned:
            await message_sent.pin(reason="Bot deepcopy")

    async def send_message(self, channel, message):

        self.message = message
        files = []
        for at in self.message.attachments:
            file = await at.to_file(spoiler=at.is_spoiler())
            files.append(file)

        embed = self.embed_template
        errors = []
        try:
            message_sent = await channel.send(embed=embed, files=files)
            await self.check_pin(message_sent)
        except (HTTPException, InvalidArgument) as e:
            errors.append([message, e])
        
        pprint(errors)
