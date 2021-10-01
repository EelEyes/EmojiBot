#!/usr/bin/env python3
#All the imports
import gc
import json
import urllib.request
from PIL import Image as pillow
import os
import re

import nest_asyncio
import discord
from discord.ext import tasks,commands
from keys import *

# For some reason setting it up this way allows for easier checking of ID's
intents = discord.Intents.default()
intents.members = True
#intents.guilds = False
intents.bans = False
intents.emojis = False
intents.integrations = False
intents.webhooks = False
intents.invites = False
intents.voice_states = False
#intents.guild_messages = False
#intents.dm_messages = False
#intents.guild_reactions = False
intents.dm_reactions = False
intents.guild_typing = False
intents.dm_typing = False
bot = commands.Bot(command_prefix='e!',intents=intents)

json_path = "emoji_list.json"

help_diamond_emoji = ":large_blue_diamond:"
help_new_emoji = ":new:"

help_icon = "https://www.clipartmax.com/png/middle/322-3227920_question-mark-png-question-mark-hover-icon.png"
help_color = 0x4AA1FE

nest_asyncio.apply()

bot.remove_command('help')

guild_index = 0

@bot.event
async def on_ready(): #Prints Server name and user ID's for those connected on startup
    global guild_index
    for guild in bot.guilds:
        #print(guild.name)
        if guild.name == GUILD:
            guild_index = bot.guilds.index(guild)
            #print(bot.guilds[guild_index].name)
            #print('yp')
            break

# Better help menu
@bot.command(name='help',pass_context=True,ignore_extra=False)
async def emoji_help(ctx): #Displays interactive help menu that shows user available commands
    await ctx.message.delete()
    commands_dict = {
        'help': "Review all of Emojibot's commands (both of them)",
        'NEWsend_<type>_<quantity>': 'Sends [quantity] emojis of chosen [type]. [quantity] defaults to 1. [type] must be "guh", "cry", "stare" or "scare". Others can be added.',
        'NEWreact_<type>': 'Reacts to the most recent message in this channel with emoji of chosen [type].  [type] must be "guh", "cry", "stare" or "scare". Others can be added.',
        'NEWadd_<type>': 'Adds the linked image as an emoji of [type] (must attach image to this message to work)',
        'NEWlist': 'Displays a list of emojis known to Emojibot'
    }
    #Sets up the help menu as a fancy embed for formatting
    help_body_text = ""
    for key in commands_dict: #Display commands (special icons for newly added ones)
        if key[:3] == "NEW":
            help_body_text += help_new_emoji+" **e!"+key[3:].replace('_',' ')+"**\n"
            help_body_text += commands_dict[key]+"\n\n"
        else:
            help_body_text += help_diamond_emoji+" **e!"+key.replace('_',' ')+"**\n"
            help_body_text += commands_dict[key]+"\n\n"
    embed=discord.Embed(title="",description=help_body_text,color=help_color)
    embed.set_author(name="Help Menu", icon_url=help_icon)
    help = await ctx.send(embed=embed)
    gc.collect()
    return

# Send COMMAND
@bot.command(name='send',ignore_extra=False)
async def emoji_send(ctx,type,quantity='1'):
    emoji_thresh = 54
    await ctx.message.delete()
    with open(json_path,'r') as file:
        emoji_dict = json.load(file)
    #print('test')
    if quantity.isdigit(): # Need Number for quantity
        #print(int(quantity))
        if int(quantity) > 0: # Number has to be positive
            #print("think")
            num_emoji = int(quantity)
            if num_emoji > 9999:
                await ctx.send("No.")
                gc.collect()
                return
        else:
            await ctx.send("Stop trying to break me :'(")
            gc.collect()
            return
    else:
        await ctx.send("Stop trying to break me :'(")
        gc.collect()
        return
    #print('wut')
    while num_emoji > emoji_thresh:
        if type.lower() in emoji_dict:
            await ctx.send(emoji_dict[type.lower()]*emoji_thresh)
        else:
            await ctx.send("I don't have **%s** yet, but maybe you can add it?" % type.lower())
            gc.collect()
            return
        num_emoji = num_emoji - emoji_thresh
    if type.lower() in emoji_dict:
        await ctx.send(emoji_dict[type.lower()]*num_emoji)
    else:
        await ctx.send("I don't have **%s** yet, but maybe you can add it?" % type.lower())
        gc.collect()
        return
    gc.collect()
    return

# React
@bot.command(name='react',ignore_extra=False)
async def emoji_react(ctx,type):
    #print('hoi')
    #print(ctx.channel.last_message_id)
    await ctx.message.delete()
    with open(json_path,'r') as file:
        emoji_dict = json.load(file)
    #print(ctx.channel.last_message_id)
    async for message in ctx.channel.history(limit=1):
        nab = message.id
    message = await ctx.fetch_message(nab)
    #print(message)
    #print('test')
    if type.lower() in emoji_dict:
        await message.add_reaction(emoji_dict[type.lower()])
    else:
        await ctx.send("I don't have **%s** yet, but maybe you can add it?" % type.lower())
        gc.collect()
        return
    gc.collect()
    return

# Add
@bot.command(name='add',ignore_extra=False)
async def emoji_add(ctx,type):
    image_path = type.lower()+".png"
    await ctx.message.delete()
    if not type == re.escape(type):
        await ctx.send("The name cannot contain special characters, sorry :(")
        gc.collect()
        return
    message = ctx.message
    end_size = 128
    max_bytes = 5000000
    with open(json_path,'r') as file:
        emoji_dict = json.load(file)
    if len(emoji_dict) >= 50:
        await ctx.send("I already have too many emojis. See **e!list** for what is available and ask the dev for help if you still want to add something.")
        gc.collect()
        return
    if type.lower() in emoji_dict:
        await ctx.send("I already have an emoji of type **%s**. See **e!list** for details and/or name your emoji something else." % type.lower())
        gc.collect()
        return
    if len(message.attachments) < 1:
        await ctx.send("You need to actually attach an image to the message to add it as an emoji.")
        gc.collect()
        return
    #print(message.attachments[0].url,message.attachments[0].size)
    if(message.attachments[0].size > max_bytes):
        await ctx.send("The image you gave me is too big; please make a smaller version and try again!")
        gc.collect()
        return
    #print('boob')
    with open(image_path,'wb') as file:
        await message.attachments[0].save(file)
    image = pillow.open(image_path)
    [x,y] = image.size
    if x > end_size and y > end_size:
        if x > y:
            scale = end_size/x
        else:
            scale = end_size/y
        width = int(x * scale)
        height = int(y * scale)
        size = (width,height)
        resized = image.resize(size)
    else:
        resized = image
        #print("already right")
    resized.save(image_path)
    with open(image_path, 'rb') as file:
        resized = file.read()
    tmp = await bot.guilds[guild_index].create_custom_emoji(name = type.lower(),image = resized)
    #print(str(tmp))
    emoji_dict[type.lower()] = str(tmp)
    with open(json_path,'w') as file:
        json.dump(emoji_dict,file)
    os.remove(image_path)
    await ctx.send("I have successfully added **%s** to my list of emotes!" % type.lower())
    await ctx.send(emoji_dict[type.lower()])
    gc.collect()
    return

@bot.command(name='delete',ignore_extra=True)
async def emoji_delete(ctx,type):
    await ctx.message.delete()
    #print(ctx.message.author.id, DEV_ID)
    if not ctx.message.author.id == DEV_ID:
        await ctx.send("You don't have permission to do that, silly.")
    else:
        with open(json_path,'r') as file:
            emoji_dict = json.load(file)
        if type.lower() in emoji_dict:
            del emoji_dict[type.lower()]
            dev_user = await bot.fetch_user(DEV_ID)
            await dev_user.create_dm()
            await dev_user.dm_channel.send("You have to remove **%s** emoji" % type.lower())
            with open(json_path,'w') as file:
                json.dump(emoji_dict,file)
        else:
            await ctx.send("Can't delete what I don't have.")
    gc.collect()
    return

# List
@bot.command(name='list',ignore_extra=True)
async def emoji_list(ctx):
    await ctx.message.delete()
    with open(json_path,'r') as file:
        emoji_dict = json.load(file)
    list_body_text = ""
    for key in emoji_dict:
        list_body_text += key+": "+emoji_dict[key]+"\n"
    embed=discord.Embed(title="",description=list_body_text,color=help_color)
    embed.set_author(name="List of Emojis", icon_url=help_icon)
    help = await ctx.send(embed=embed)
    gc.collect()
    return

# ERROR EVENTS (COMMAND NOT FOUND, MISSING ARGUMENT, MISSING ROLE, OTHER)
@bot.event
async def on_command_error(ctx, error): #Handles any command errors
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument): #Missing an argument
        await ctx.send("You need to include more arguments. See **e!help** for details.")
    else:
        print(error)
    gc.collect()
    return


bot.run(TOKEN)
