# =================================
# Imports
# =================================
from discord.ext import commands
from discord.ext import tasks

import asyncio
import datetime
import discord
import logging
import os

import scheduler
import util


# =================================
# Logging setup
# =================================
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
COMMAND_PREFIX = '/'

NOTIFICATION_FREQUENCY = {'minutes': 30.0}
RESET_TIME = datetime.time(4, 20, 0, 0)
NOTIFICATION_START = datetime.time(21, 30, 0, 0)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(COMMAND_PREFIX), 
                   intents=intents)

sch: scheduler.Scheduler = None
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
  sch = scheduler.Scheduler(users)

  server_str = """

            ██████╗██████╗███╗   ███╗██████╗███╗   ████████╗              
            ██╔═══████╔══██████╗ ██████╔═══██████╗  ████╔══██╗             
            ██║   ████████╔██╔████╔████║   ████╔██╗ ████║  ██║             
            ██║   ████╔══████║╚██╔╝████║   ████║╚██╗████║  ██║             
            ╚██████╔██║  ████║ ╚═╝ ██╚██████╔██║ ╚██████████╔╝             
            ╚═════╝╚═╝  ╚═╚═╝     ╚═╝╚═════╝╚═╝  ╚═══╚═════╝              
   
    ████████╗  ██╗██████╗██████╗███████╗        ███╗   ███╗██████╗██████╗ 
    ██╔════██║  ████╔═══████╔══████╔════╝        ████╗ ██████╔════╝██╔══██╗
    ██║    █████████║   ████████╔█████╗          ██╔████╔████║  █████████╔╝
    ██║    ██╔══████║   ████╔══████╔══╝          ██║╚██╔╝████║   ████╔══██╗
    ╚████████║  ██╚██████╔██║  █████████╗        ██║ ╚═╝ ██╚██████╔██║  ██║
    ╚═════╚═╝  ╚═╝╚═════╝╚═╝  ╚═╚══════╝        ╚═╝     ╚═╝╚═════╝╚═╝  ╚═╝

Registered Users:
{}

Configured to notify every {} {}.

Now Serving.\n""".format('\n'.join(u.nick or u.name for u in users),
                         list(NOTIFICATION_FREQUENCY.values())[0],
                         list(NOTIFICATION_FREQUENCY.keys())[0])

  logger.info(server_str)
  print(server_str, flush=True)
  notify.start()
  return

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

'''
@bot.command(name='create_bundle', help='Adds specified bundle and adds it to the rotation')
async def FUNCTION_NAME(ctx):
  send user empty prompt export as "new_bundle"
  adds bundle "new_bundle", run set rotation function
  await ctx.message.channel.send('Bundle "y" has been added to rotation and bundles')
  return

@bot.command(name='update_bundle', help='Enter new responsibilities for selected bundle')
async def FUNCTION_NAME(ctx):
  send user dropdown of "bundles"
    export decision as "chosen_bundle"
  send user empty prompt
    export text as string"new_responsibilities"
    replace string"responsibilities" of "chosen_bundle" with string"new_responsibilities"
  await ctx.message.channel.send('Bundle "z" is now responsible for "responsibilities"')
  return

@bot.command(name='read_bundles', help='Lists all bundles and what they're responsible for')
async def show_bundle(ctx):
  collect all bundle and
#   format into varible named "output"
  await ctx.message.channel.send(print "output")
  return

@bot.command(name='delete_bundle', help='Delete specified bundle and removes it from rotation')
async def FUNCTION_NAME(ctx):
  send user ('what bundle would you like to delete')
  send user dropdown of "bundles"
    delete chosen bundle
  run set rotation function
  await ctx.message.channel.send('Bundle "x" has been deleted and removed from rotation')
  return

@bot.command(name='show_rotation', help='Displays the current rotation of Who does What')
async def FUNCTION_NAME(ctx):
  format "rotations" 
  await ctx.message.channel.send(print "rotations")
  return

@bot.command(name='set_rotation', help='Select what weeks rotation you'd like it set to')
async def rotation_weeks(ctx):
  send user dropdown of "weeks"
  run set rotation function
  await ctx.message.channel.send(MESSAGE_TEXT)
  return

@bot.command(name='complete', help='Marks the users assigned tasks as completed')
async def complete(ctx):
  set user task as complete
  await ctx.message.channel.send(you did good nigga)
  return
'''

@bot.command(name='today', help='Return the person who is on-call today')
async def on_call_today(ctx):
  await ctx.message.channel.send(
    '<@{}> is responsible for the kitchen tonight!'.format(sch.on_call.id))
  return

  
@bot.command(name='schedule', help='List the schedule for the seven days')
async def schedule(ctx):
  await ctx.message.channel.send('```{}```'.format(sch.generate_schedule()))
  return


@bot.command(name='swap', help='Swap on call position with chosen person')
async def swap(ctx, member: discord.Member):
  try:
    sch.swap(ctx.message.author, member)
  
    await ctx.message.channel.send('Users have been switched! The new schedule '
                                  'should be as follows:')
    await ctx.message.channel.send('```{}```'.format(sch.generate_schedule()))
  except ValueError:
    await ctx.message.channel.send('You can\'t swap with yourself!')
  except:
    await ctx.message.channel.send('There was an error when trying to swap.')

  return

  
@bot.command(name='signoff', help='Sign off the on-call member for today')
async def signoff(ctx):
  oncall = sch.on_call

  if ctx.message.author == oncall:
    await ctx.message.channel.send('You can\'t sign off yourself!')
    logger.warning('{} tried to sign off themselves'.format(ctx.message.author))
    return

  sch.signoff()
  await ctx.message.channel.send(
    '<@{}> has been signed off for tonight! <@{}> is responsible for '
    'the kitchen next.'.format(oncall.id, sch.on_call.id))
  return


@tasks.loop(**NOTIFICATION_FREQUENCY)
async def notify():
  curr_time = datetime.datetime.now().time()

  if not sch.signed_off and (curr_time >= NOTIFICATION_START or \
     (curr_time <= RESET_TIME)):
    await _default_channel.send(
      'Reminder that <@{}> is responsible for the kitchen tonight!'.format(
        sch.on_call.id))
  elif sch.signed_off and curr_time >= RESET_TIME:
    sch.signed_off = False
  else:
    logger.info('Notification suppressed.')

  logger.info('{} has been notified.'.format(util.discord_name(sch.on_call)))
  return


@notify.before_loop
async def notifications_init():
  """Sleep so that the notifications start on the hour."""
  next_hour = datetime.datetime.now()
  next_hour = next_hour.replace(
    minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)

  delta = next_hour - datetime.datetime.now()
  logger.info('Sleeping {} seconds before activating notifications'.format(
    delta.total_seconds()))
  await asyncio.sleep(delta.total_seconds())
  return

  
if __name__ == '__main__':
  util.load_env()
  bot.run(os.getenv('TOKEN'))
