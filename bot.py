#Nanobot 2.0 | format based upon Red for modularity | https://github.com/Twentysix26/Red-DiscordBot
from discord.ext import commands
from optparse import OptionParser
import asyncio
import datetime
import time
import discord
import logging
import logging.handlers
import os
import sys
import traceback
import requests
from cogs.utils.dataIO import dataIO
from cogs.utils.settings import Settings
from cogs.utils.embed import Embeds

clist = ['cogs.core', 'cogs.dev', 'cogs.audio', 'cogs.general', 'cogs.overwatch', 'cogs.moderation', 'cogs.error_handler']
errors = []
cmds_this_session = []

class objects:
	class Command:
		def __init__(self, name, original):
			self.name = name
			self.original = original

class Bot(commands.Bot):
	def __init__(self, *args, **kwargs):

		def prefix_mgr(bot, message):
			return bot.settings.get_prefixes(message.server)

		self.cmds_this_session = []
		self.errors = []
		self.start_time = []
		self.cmds_this_session = []
		self.errors = []
		self.start_time = []
		self.settings = Settings()
		self.uptime = datetime.datetime.utcnow()
		self.logger = logger_config(self)
		self.embeds = Embeds()
		self.partners = []
		self.partnered_guilds = []
		self.badges = {
		'partner':'<:partner:356053840799203330>',
		'staff':'<:staff:356053841013112833>',
		'dev':'<:dev:356053840975364097>',
		'voter':'<:voter:356053840996466699>',
		'retired':'<:retired:343110154834935809>',
		'bronze':'<:ow_bronze:338113846432628736>',
		'silver':'<:ow_silver:338113846734618624>',
		'gold':'<:ow_gold:338113846533292042>',
		'platinum':'<:ow_platinum:338113846550200331>',
		'diamond':'<:ow_diamond:338113846172450818>',
		'master':'<:ow_master:338113846377971719>',
		'grandmaster':'<:ow_grandmaster:338113846503931905>'}
		super().__init__(*args, command_prefix=prefix_mgr, **kwargs)

def initialize(bot_class=Bot):
	bot = bot_class(description="A bot to help fill your server with music, Overwatch, and more!")

	import __main__
	__main__.settings = bot.settings

	for extension in clist:
		try:
			check_folders()
			bot.load_extension(extension)
			print("Loaded {}".format(str(extension)))
		except Exception as e:
			print("{}: {}".format(type(e).__name__, e))

	@bot.event
	async def on_message(message):
		if (message.content.startswith('!!') and not message.content.startswith('!!!')) or message.content.startswith('nano '):
			bot.logger.info(message.content)
			ccmds = None
			bot.cmds_this_session.append(objects.Command(message.content.split()[0], message.content))
			if message.content == "!!" or message.content == "nano ":
				await bot.send_message(message.channel, ":thinking: Why did you even think that would work? Type `!!help` for help.")
			else:
				await bot.process_commands(message)

	@bot.event
	async def on_server_join(server):
		try:
			post_stats()
			await bot.change_presence(game=discord.Game(name='!!help • {} Guilds'.format(len(bot.servers))), status=discord.Status.online)
		except:
			logger.error(traceback.format_exc())
			logging.info("Joined server {0.name} (ID: {0.id})".format(server))
		try:
			await bot.send_message(server.default_channel, ':wave: Hi, I\'m NanoBot! For help on what I can do, type `!!help`. Join the NanoBot Discord for support and updates: https://discord.io/nano-bot')
		except:
			pass
		await bot.send_message(bot.get_channel(id="334385091482484736"), embed=bot.embeds.server_join(server))

	@bot.event
	async def on_server_remove(server):
		try:
			post_stats()
			await bot.change_presence(game=discord.Game(name='!!help • {} Guilds'.format(len(bot.servers))), status=discord.Status.online)
		except:
			logger.error(traceback.format_exc())
		logging.info("Left server {0.name} (ID: {0.id})".format(server))
		await bot.send_message(bot.get_channel(id="334385091482484736"), embed=bot.embeds.server_leave(server))

	@bot.event
	async def on_ready():
		bot.start_time = time.time()
		print("Bot Initialized...")
		print(f"Logged in as {bot.user.name} with the ID of {bot.user.id}")
		post_stats()
		await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=f"!!help • {len(bot.guilds)}"))

def post_stats():
	payload = {"server_count":int(len(bot.servers))}
	headers = {"Authorization":str(bot.settings.discordbotsorg_token)}
	r = requests.post("https://discordbots.org/api/bots/{}/stats".format(str(bot.user.id)), data=payload, headers=headers)
	if not(r.status_code == 200 or r.status_code == 304):
		bot.logger.error("2/Failed to post server count: " + str(r.status_code))
		bot.logger.error("The following data was returned by the request:\n{}".format(r.text))

def check_folders():
    folders = ("data", "data/bot", "cogs", "cogs/utils")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder(s)...")
            os.makedirs(folder)

def logger_config(bot):
	logger = logging.getLogger("bot")
	logger.setLevel(logging.INFO)
	log_format = logging.Formatter(
		'%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
		'%(message)s', datefmt='[%I:%M:%S %p]')
	stdout_handler = logging.StreamHandler(sys.stdout)
	stdout_handler.setFormatter(log_format)
	stdout_handler.setLevel(logging.INFO)
	logger.setLevel(logging.INFO)
	file_handler = logging.handlers.RotatingFileHandler(
		filename='data/bot/bot.log', encoding='utf-8', mode='a', maxBytes=10**8, backupCount=5)
	file_handler.setFormatter(log_format)
	logger.addHandler(file_handler)
	logger.addHandler(stdout_handler)
	api_logger = logging.getLogger("discord")
	api_logger.setLevel(logging.WARNING)
	api_handler = logging.FileHandler(
		filename='data/bot/discord.log', encoding='utf-8', mode='a')
	api_handler.setFormatter(logging.Formatter(
		'%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
		'%(message)s', datefmt='[%I:%M:%S %p]'))
	api_logger.addHandler(api_handler)

def main(bot):
	check_folders()
	bot.run(bot.settings.token)

if __name__ == "__main__":
	bot = initialize()
	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(main(bot))
	except discord.LoginFailure:
		bot.logger.error(traceback.format_exc())
	except KeyboardInterrupt:
		loop.run_until_complete(bot.logout())
	except Exception as e:
		bot.logger.exception("Fatal Exception", exc_info=e)
		loop.run_until_complete(bot.logout())
	finally:
		loop.close()
		exit(0)
