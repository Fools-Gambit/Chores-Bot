# =================================
# Imports
# =================================
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands

import asyncio
import datetime
import discord
import logging
import os

from scheduler import ChoreScheduler
import util


# =================================
# Logging setup
# =================================
# TODO: Adjust the logging functionality
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
  '[%(levelname)s] {%(funcName)s | %(filename)s} %(asctime)s:  %(message)s')

file_handler = logging.FileHandler(
  filename=util.get_logs_folder() / 'kitchen-chores-bot-{}.log'.format(
    datetime.datetime.now()),
  encoding='utf-8', mode='w')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARNING)
logger.addHandler(console_handler)


# =================================
# Bot parameters
# =================================

NOTIFICATION_FREQUENCY = {'minutes': 30.0}
RESET_TIME = datetime.time(4, 20, 0, 0)
NOTIFICATION_START = datetime.time(21, 30, 0, 0)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(intents=intents, command_prefix='/')

sch: ChoreScheduler = None
_default_channel = None


# =================================
# Bot Commands
# =================================
@bot.event
async def on_ready():
  global _default_channel
  _guild = next(filter(lambda g: g.id == int(os.getenv('GUILD')), bot.guilds))
  _default_channel = next(filter(lambda c: c.id == int(os.getenv('CHANNEL')), 
                      _guild.channels))
  role = next(filter(lambda r: r.id == int(os.getenv('ROLE')), _guild.roles))
  bot_role = next(filter(lambda r: r.name == 'bot', _guild.roles))

  users = []
  for member in _guild.members:
    if role in member.roles and bot_role not in member.roles:
      users.append(member)

  global sch
  sch = ChoreScheduler()

  for user in users:
    sch.add_user(user.id)

  server_str = """

Registered Users:
{}

Configured to notify every {} {}.

Now Serving.\n""".format('\n'.join(u.nick or u.name for u in users),
                         list(NOTIFICATION_FREQUENCY.values())[0],
                         list(NOTIFICATION_FREQUENCY.keys())[0])

  logger.info(server_str)
  print(server_str, flush=True)
  guild = discord.Object(id=int(os.getenv('GUILD')))
  bot.tree.clear_commands(guild=guild)
  bot.tree.copy_global_to(guild=guild)
  synced = await bot.tree.sync(guild=guild)
  print(f'{len(synced)} slash commands synced!')

#Bundles
#   Kitchen (a) - countertops, stove, sink, airfryer, microwave, fridge, oven
#   Floors (b) - sweep, mop, vacuum
#   Utility (c) - windows, window sills, doors, washer, dryer, cabinets
#   Surfaces (d) - table, coffee table, bookshelves, entertainment center

#Rotation, Saturdays only, Rotates Weekly
#   Week 1 Garrett A, Estelle B, Jakob C, Kiera D
#   Week 2 Garrett B, Estelle C, Jakob D, Kiera A
#   Week 3 Garrett C, Estelle D, Jakob A, Kiera B
#   Week 4 Garrett D, Estelle A, Jakob B, Kiera C
#   repeat cycle

#Tracker/Notifications
#   Bot will notify each individual with thier respective "Bundle" Saturday 10am
#   At 4pm a notifaction will go off to each individual who has not logged thier chores as "Complete"

#Commands
#   "Bundles" - Lists all bundles and what they're responsible for
#     create bundle, update bundle, read bundle, delete bundle   
#   "Rotation" - Will post the current week and the full rotation
#     update rotation, read rotation
#   "Complete" - Will silence notifications until next week

# Create/update/delete bundles (I recommend naming them better than bundle 1 (kitchen, floors, etc) ) Define better elsewhere
# Get chore doers from a specific role OR from a command? Which one?
# Warn/adapt if the number of bundles doesn't match with the number of chore doers

# Force sync for testing
@bot.command()
async def sync(ctx):
    guild = discord.Object(id=ctx.guild.id)
    ctx.bot.tree.copy_global_to(guild=guild)
    synced = await ctx.bot.tree.sync(guild=guild)
    await ctx.send(f"{len(synced)} slash commands synced!")

### Bundle CRUD ###

@bot.hybrid_command(name='create_bundle', description='Adds specified bundle and adds it to the rotation')
@app_commands.describe(bundle='the chore bundle')
async def create_bundle(ctx: commands.Context, bundle: str):
  parsed = bundle.split()
  sch.add_chore(parsed)
  # Run the set_rotation function
  await ctx.send(f'Bundle {parsed[0]} has been added to rotation and bundles')

async def bundle_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    print("I'm completing!")
    options = sch.data.chores.keys()
    return [app_commands.Choice(name=option, value=option) for option in options if option.lower().startswith(current.lower())][:25]

@bot.hybrid_command(name='remove_bundle', description='Remove specified bundle from the list and rotation')
@app_commands.describe(bundle='the bundle to remove')
@app_commands.autocomplete(bundle=bundle_autocomplete)
async def remove_bundle(ctx: commands.Context, bundle: str):
  await ctx.send(f'Bundle {bundle} has been removed from the rotation!')
#   send user ('what bundle would you like to delete')
#   send user dropdown of "bundles"
#     delete chosen bundle
#   run set rotation function
#   await ctx.send('Bundle "x" has been deleted and removed from rotation')


@bot.hybrid_command(name='update_bundle', description='Update existing chore bundle with new responsibilities')
async def update_bundle(ctx: commands.Context):
  pass
#   send user dropdown of "bundles"
#     export decision as "chosen_bundle"
#   send user empty prompt
#     export text as string"new_responsibilities"
#     replace string"responsibilities" of "chosen_bundle" with string"new_responsibilities"
#   await ctx.send('Bundle "z" is now responsible for "responsibilities"')

@bot.hybrid_command(name='show_bundles', description='List all bundles and their chores')
async def show_bundles(ctx: commands.Context):
  pass
#   collect all bundle and
# #   format into varible named "output"
#   await ctx.send(print "output")

###################

'''
@bot.hybrid_command(name='show_rotation', help='Displays the current rotation of Who does What')
async def show_rotation(ctx: commands.Context):
  format "rotations" 
  await ctx.send(print "rotations")

@bot.hybrid_command(name='set_rotation', help='Select what weeks rotation you'd like it set to')
async def set_rotation(ctx: commands.Context):
  send user dropdown of "weeks"
  run set rotation function
  await ctx.send(MESSAGE_TEXT)

@bot.hybrid_command(name='complete', help='Marks the users assigned tasks as completed')
async def complete(ctx: commands.Context):
  set user task as complete
  await ctx.send(you did good nigga)
'''


# @tasks.loop(**NOTIFICATION_FREQUENCY)
# async def notify():
#   curr_time = datetime.datetime.now().time()

#   if not sch.signed_off and (curr_time >= NOTIFICATION_START or \
#      (curr_time <= RESET_TIME)):
#     await _default_channel.send(
#       'Reminder that <@{}> is responsible for the kitchen tonight!'.format(
#         sch.on_call.id))
#   elif sch.signed_off and curr_time >= RESET_TIME:
#     sch.signed_off = False
#   else:
#     logger.info('Notification suppressed.')

#   logger.info('{} has been notified.'.format(util.discord_name(sch.on_call)))


# @notify.before_loop
# async def notifications_init():
#   """Sleep so that the notifications start on the hour."""
#   next_hour = datetime.datetime.now()
#   next_hour = next_hour.replace(
#     minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)

#   delta = next_hour - datetime.datetime.now()
#   logger.info('Sleeping {} seconds before activating notifications'.format(
#     delta.total_seconds()))
#   await asyncio.sleep(delta.total_seconds())
  
if __name__ == '__main__':
  util.load_env()
  bot.run(os.getenv('TOKEN'))