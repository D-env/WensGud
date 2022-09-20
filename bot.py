import os
import random
import re
from time import sleep

from dotenv import load_dotenv
from discord.ext import commands
import discord

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
time_regex = r"([0|1]\d[0-5]\d,[0|1]\d[0-5]\d)|(2[0-3][0-5]\d,[0|1]\d[0-5]\d)|(2[0-3][0-5]\d,2[0-3][0-5]\d)|([0|1]\d[0-5]\d,2[0-3][0-5]\d)"

members = {}
events = {}

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# **************************
# ******* BOT EVENTS *******
# **************************


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    for guild in bot.guilds:
        if guild == GUILD:
            break

    for member in guild.members:
        print(member)


# add help command, maybe include summary functionality
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to our server!'
        f'If you would like to be a part of the server scheduling, please enter the'
        f'\"!signup\" command in the scheduling text channel'
    )

# *****************************
# ******* BOT COMMANDS ********
# *****************************


# - optin command
#     allows user to opt in to scheduling functionality
#     gives stock availablity?
# - optout commands
#     allow user to opt out if previously opted in
# - available command
#     takes in user availablilty for each day
#     (overrides original stock availablility)
# - create command
#     allows user to create an event
# - cancel commands
#     allows user to cancel event
# - join commands
#     allows you to join specified event
# - leave commands
#     allows you to leave specified event

# update to use server nickname?
@bot.command(name='optin', help='This command gives you the ability to join events.')
async def opt_in(ctx):

    if ctx.author.nick:
        response = f'{ctx.author.nick} has signed up for events!'
    else:
        response = f'{ctx.author.name} has signed up for events!'

    members[ctx.author.name] = []
    print(members)

    await ctx.send(response)


@bot.command(name='optout', help='This command allows')
async def opt_out(ctx):
    if ctx.author.nick:
        response = f'{ctx.author.nick} has decided to opt out for events!'
    else:
        response = f'{ctx.author.name} has decided to opt out for events!'

    members.remove(ctx.author.name)
    print(members)
    await ctx.send(response)


@bot.command(name='availability', help='This command allows you to enter in your typical availability')
async def enter_availability(message):
    days_of_week = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    user_availability = []
    await message.channel.send(f'We hear you want to change your availability. Please enter the days you would like '
                               f'to change your availability on separated by a space. (Ex. Tuesday Friday)'
                               f' If you want to change availability for all days enter \"All\"')

    days = await bot.wait_for('message')
    if days.lower == "all":
        await message.channel.send(f'You are changing your availability for every day of the week. Please enter your '
                                   f'availability Sunday-Saturday in a similar format to the following: '
                                   f'0830,1230 1140,1440 1630,1830 1440,1540 1020,1350 0600,0700 0740,1830')
        times = await bot.wait_for('message')
        times_list = helper_check(times.content)
        if len(times_list) == 7:
            for time in times_list:
                user_availability.append(time)
    else:
        split_days = days.split(" ")
        await message.channel.send(f'You are changing your availability for {days}. Please enter your availability'
                                   f'starting with the day closest to Sunday and ending with the day closest to '
                                   f'Saturday. If you are changing your availabilty for Tuesday and Friday it would be'
                                   f'08:40,12:30 12:30,14:30')
        times = await bot.wait_for('message')
        times_list = helper_check()


    for day in days_of_week:
        sleep(1)
        await message.channel.send(f'Enter your availability on {day} ->')
        msg = await bot.wait_for('message')

        if len(helper_check(msg.content)) == 2 or msg.content == "None":
            user_availability.append(msg.content)
        else:
            # let user know invalid input and give them "None" in place
            # let them know they need to redo if they don't want None
            await message.channel.send(f'Invalid Input! Your availability for {day} is now None '
                                       f'if you want to change this redo your !availability command!')
            user_availability.append("None")

    members[message.author.name] = user_availability
    print(members)

    await message.channel.send(user_availability)


def helper_check(message):
    # 00:00
    return re.findall(time_regex, message)


@bot.command(name='create', help='This command allows a user to create a new event.')
async def create_event(ctx):
    await ctx.channel.send(f'Please enter your event name ->')
    name = await bot.wait_for('message')
    # await ctx.channel.send(f'Please enter a description for your event ->')
    # description = await bot.wait_for('message')
    # await ctx.channel.send(f'Please enter your event duration (2:40 would be 2 hours and 40 minutes ->')
    # duration = await bot.wait_for('message')

    # await ctx.channel.send(f'Please enter your event start time ->')
    # start_time = await bot.wait_for('message')
    # await ctx.channel.send(f'Please enter your event end time ->')
    # end_time = await bot.wait_for('message')

    events[name.content] = {}
    # print([ctx.author.name, name.content, description.content, duration])
    print(events)

# await create_scheduled_event(*, name, start_time, entity_type=..., privacy_level=..., channel=..., location=...,
#                              end_time=..., description=..., image=..., reason=None)¶


@bot.command(name='cancel', help='This command allows a user to cancel an event. Inlcude event name.')
async def cancel_event(ctx):
    input_list = ctx.message.content.split()
    event_name = " ".join(input_list[1:])

    if event_name in events:
        del events[event_name]
        print(events)
        await ctx.channel.send(f'You have cancelled the {event_name} event.')
    else:
        await ctx.channel.send(f'Sorry, {event_name} is not a valid event in our logs.')


@bot.command(name='join', help='This command allows a user to join an event. Include event name.')
async def join_event(ctx):
    input_list = ctx.message.content.split()
    event_name = ' '.join(input_list[1:])
    if event_name in events:
        events[event_name][ctx.author.name] = members[ctx.author.name]
        # target_event = events[event_name]
        # target_event[ctx.author.name] = members[ctx.author.name]
        print(events)
        await ctx.channel.send(f'{ctx.author.name} has joined {event_name}')
    else:
        await ctx.channel.send(f'Sorry, {event_name} is not a valid event in our logs.')


@bot.command(name='leave', help='This command allows a user to leave an event. Include event name.')
async def leave_event(ctx):
    input_list = ctx.message.content.split()
    event_name = ' '.join(input_list[1:])
    if events[event_name]:
        if ctx.author.name in events[event_name]:
            events[event_name].pop(ctx.author.name)
            await ctx.channel.send(f'{ctx.author.name} has left {event_name}')
    else:
        await ctx.channel.send(f'Sorry, {event_name} is not a valid event in our logs.')

    print(events)




@bot.command(name='hello', help='Please help me :(')
async def hello(ctx):
    greetings = [
        'Hello',
        'Hola',
        'Greetings',
    ]

    response = random.choice(greetings)
    await ctx.send(response)



@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to our server!'
        f'If you would like to be a part of the server scheduling, please enter the'
        f'\"!optin\" command in the scheduling text channel'
    )

bot.run(TOKEN)
