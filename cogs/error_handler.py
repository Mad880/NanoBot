import discord
from discord.ext import commands

def is_owner():
    async def predicate(ctx):
        return ctx.author.id == 670972734960042005 # obviously replace this with your own id
    return commands.check(predicate)

class CommandErrorHandler(commands.Cog):

	def __init__(self, bot):
		self.bot = bot


	@commands.cog.listener()
	async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.CommandNotFound)

        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not meet the requirements for running this command.')

		elif isinstance(error, commands.DisabledCommand):
			await ctx.send("This command is disabled!")

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send('I don\'t have enough permissions to do that.')

		elif isinstance(error, commands.NoPrivateMessage):
			await ctx.send("This command can't be used in private messages.")

		# if you want to add anything else, feel free to pull a request

    @commands.command(hidden=True)
    @is_owner
    async def errortest(self, ctx):
        print("Bruh!")

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))