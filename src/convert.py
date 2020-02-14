from discord.ext import commands


def numeralconvert(message):
    fro, to = message.split(" to ")
    val = int(fro.split(" ")[0])
    if to == "hex":
        response = f"The decimal value of `{val}` is: `{hex(val)}` in hexadecimal."
    elif to == "octal":
        response = f"The decimal value of `{val}` is: `{oct(val)}` in octal."
    elif to == "binary":
        response = f"The decimal value of `{val}` is: `{bin(val)}` in binary."
    else:
        response = f"I don't understand."

    return response


class Convert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="convert")
    async def convert(self, ctx, *, message: str):
        value_table = ['decimal', 'hex', 'octal', 'binary']
        if '"' in message:
            pass
        elif any(x in message for x in value_table):
            await ctx.send(numeralconvert(message))
            return

        fro, to = message.split(" to ")
        val, fro = fro.split(" ")
        print(fro)
        print(to)

        await ctx.send('{:,P}'.format(ctx.bot.quantity(float(val), fro).to(to)))


def setup(bot):
    bot.add_cog(Convert(bot))
