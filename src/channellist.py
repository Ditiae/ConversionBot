import discord
from discord.ext import commands


async def getchannellist(bot, sortchars):
    bot.paginator.clear()
    f = open("channels.txt", "r", encoding='utf16')
    lines = f.readlines()
    lines.sort(key=str.lower)
    for x in lines:
        if sortchars == '':
            bot.paginator.add_line(x)
        elif x[0].lower() in sortchars:
            bot.paginator.add_line(x)
    if len(bot.paginator.pages) == 0:
        bot.paginator.add_line("No channels found.")


async def getsearchresponse(bot, query):
    bot.paginator.clear()
    f = open("channels.txt", "r", encoding='utf16')
    lines = f.readlines()
    lines.sort(key=str.lower)
    for x in lines:
        if query.lower() in x.rsplit(" - ", 1)[0].lower():
            bot.paginator.add_line(x)
    if len(bot.paginator.pages) == 0:
        bot.paginator.add_line("No channels found.")


class ChannelList(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="channelsfile", aliases=["chanout", "gibfile"])
    async def channelsfile(self, ctx):
        await ctx.send(file=discord.File('channels.txt'))

    async def updatemsg(self, msg):
        reactions = [u"\u25C0", u"\u25B6"]
        page = self.bot.page
        pages = self.bot.paginator.pages
        await msg.clear_reactions()
        await msg.edit(content=f'{pages[page]}\n\t\tYou are viewing page {page + 1} of {len(pages)}')
        if page == 0:
            await msg.add_reaction(reactions[1])
        elif page == len(pages) - 1:
            await msg.add_reaction(reactions[0])
        else:
            for reaction in reactions:
                await msg.add_reaction(reaction)

    @commands.command(name="listchannels", aliases=["listchan", "lchan"])
    async def listchannels(self, ctx, sortchars=''):
        await getchannellist(ctx.bot, sortchars)
        ctx.bot.page = page = 0
        pages = ctx.bot.paginator.pages
        if len(pages) == 1:
            await ctx.send(content=f'{pages[page]}')
            return
        else:
            msg = await ctx.send(content=f'{pages[page]}\n\t\tYou are viewing page {page + 1} of {len(pages)}')
        await msg.add_reaction(u"\u25B6")

    @commands.command(name="search")
    async def search(self, ctx, *, query):
        if len(query) < 3:
            await ctx.send("Search request must be at least 3 characters in length.")
            return
        await getsearchresponse(ctx.bot, query)
        page = ctx.bot.page
        pages = ctx.bot.paginator.pages
        if len(pages) == 1:
            await ctx.send(content=f'{pages[page]}')
            return
        else:
            msg = await ctx.send(content=f'{pages[page]}\n\t\tYou are viewing page {page + 1} of {len(pages)}')
        await msg.add_reaction(u"\u25B6")

    @commands.command(name="ahelp")
    async def ahelp(self, ctx):
        await ctx.send("use channel link")

    @commands.command(name="giverole")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def giverole(self, ctx):
        role = discord.utils.get(ctx.message.author.guild.roles, name="YT Archive")
        user = ctx.message.author
        if role not in ctx.message.author.roles:
            await user.add_roles(role)
            await ctx.send("Role given, enjoy.")
        else:
            await user.remove_roles(role)
            await ctx.send("Role removed, enjoy.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if not reaction.message.author.bot:
            return
        if "You are viewing page" not in reaction.message.content:
            return
        if reaction.emoji == "◀":
            if self.bot.page == 0:
                return
            else:
                self.bot.page -= 1
        elif reaction.emoji == "▶":
            self.bot.page += 1
        await self.updatemsg(reaction.message)


def setup(bot):
    bot.add_cog(ChannelList(bot))
