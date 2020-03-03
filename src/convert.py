from discord.ext import commands
from pint import UndefinedUnitError, DimensionalityError


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
        val = val.replace(",", "")
        print(fro)
        print(to)
        try:
            float(val)
        except ValueError:
            await ctx.send("That is not an accepted quantity.")
            return
        try:
            await ctx.send('{:,P}'.format(ctx.bot.quantity(float(val), fro).to(to)))
        except UndefinedUnitError as e:
            await ctx.send(f"You input an incorrect unit: {str(e)}.")
            return
        except DimensionalityError as e:
            await ctx.send(f"Those units have incorrect dimensions: {str(e)}.")
            return


def setup(bot):
    bot.add_cog(Convert(bot))
