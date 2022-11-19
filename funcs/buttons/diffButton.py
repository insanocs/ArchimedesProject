from typing import List

import disnake
from disnake.ext import commands


class DiffButton(disnake.ui.View):
    def __init__(self, url):
        super().__init__()
        self.url = url
        # Link buttons cannot be made with the decorator
        # Therefore we have to manually create one.
        # We add the quoted url to the button, and add the button to the view.
        self.add_item(disnake.ui.Button(label="Teleport", url=url))

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @disnake.ui.button(label="Chunks", style=disnake.ButtonStyle.green, disabled=False)
    async def chunks(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.chunks.disabled = True
        await interaction.response.edit_message(view=self)
        embed = disnake.Embed(color=0xFF0000)
        embed.set_author(
            name="Template chunks",
            icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA",
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256"
        )
        embed.add_field(name="Chunks:", value="number of chunks", inline=False)
        embed.set_image(file=disnake.File("bigchunks.png"))
        embed.set_footer(text="sent at")
        await interaction.followup.send(embed=embed)
        # self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @disnake.ui.button(label="Data", style=disnake.ButtonStyle.primary, disabled=False)
    async def data(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.data.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("Cancelling", file=disnake.File("plot.png"))
        # self.stop()
