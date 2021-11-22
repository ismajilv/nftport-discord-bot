import os

from discord.ext import commands

from bot.api import NftPortApi
from bot.constants import TIMEOUT_COMMAND

bot = commands.Bot(command_prefix="!")
api = NftPortApi()


async def _wait_for_text(ctx: commands.Context, ask: str):
    def check(message):
        return message.author == ctx.author

    await ctx.send(ask)
    msg = await bot.wait_for("message", check=check, timeout=TIMEOUT_COMMAND)

    return msg.content


async def _wait_for_attachment(ctx: commands.Context, ask: str):
    def check(message):
        return (
            message.author == ctx.author
            and bool(message.attachments)
            and len(message.attachments) == 1
        )

    await ctx.send(ask)
    msg = await bot.wait_for("message", check=check, timeout=TIMEOUT_COMMAND)

    image_url = msg.attachments[0].url
    image_name = image_url.split("/")[-1]
    image_name = image_name.split(".")[0]

    return image_url, image_name


@bot.command(help=" Interactive NFT minting with the help of NFTPort API")
async def mint(ctx: commands.Context):
    image_url, image_name = await _wait_for_attachment(
        ctx, "Attach the image you would like to mint"
    )
    to_address = await _wait_for_text(ctx, "Provide the wallet address to mint to")
    api_key = await _wait_for_text(ctx, "Provide the NFTPort API key")

    await ctx.send("PLease wait while we mint...")

    transaction_external_url = await api.mint_with_url(
        api_key=api_key,
        file_url=image_url,
        to_address=to_address,
        description=f"{ctx.author}'s NFT minted with NFTPort API",
        name=image_name,
    )

    if transaction_external_url:
        await ctx.send(
            f"Successfully minted! Check out your newly minted NFT's transaction details at {transaction_external_url}"
        )
    else:
        await ctx.send("Could not mint!")


@mint.error
async def mint_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandInvokeError) and "TimeoutError" in str(error):
        await ctx.send("Slow to answer, please try again from scratch")
    else:
        await ctx.send("Sorry, something went wrong...")


bot.run(os.environ.get("BOT_TOKEN"))
