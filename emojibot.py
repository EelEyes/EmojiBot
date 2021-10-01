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

# This sets up the bot and teaches it what it can do and how to take commands
bot = commands.Bot(command_prefix='e!',intents=intents)

# Some global variables
json_path = "emoji_list.json" # relative path to json file

help_diamond_emoji = ":large_blue_diamond:" #emojis for the help menu
help_new_emoji = ":new:" #emojis for the help menu

help_icon = "https://www.clipartmax.com/png/middle/322-3227920_question-mark-pn\
g-question-mark-hover-icon.png" # icon for the help menu
help_color = 0x4AA1FE # color for the help menu embed

guild_index = 0 # keep track of where the server that holds our emojis is

nest_asyncio.apply() # I'm not sure I remember what this does

bot.remove_command('help') # lets us make a better help command


@bot.event
async def on_ready(): # As soon as the bot has sentience
    global guild_index
    for guild in bot.guilds: # Look through all the servers you are in
        #print(guild.name)
        if guild.name == GUILD: # When it finds the one where emojis are kept
            guild_index = bot.guilds.index(guild) # Remember where it is
            #print(bot.guilds[guild_index].name)
            #print('yp')
            break

# Better help menu command
@bot.command(name='help',pass_context=True,ignore_extra=False)
async def emoji_help(ctx): #Displays help menu that shows user available commands
    await ctx.message.delete() # Deletes the user's command for streamlined visuals
    commands_dict = { # Dictionary of the commands for EmojiBot
        'help': "Review all of Emojibot's commands (both of them)",
        'send_<type>_<quantity>': 'Sends [quantity] emojis of chosen [type]. [quantity] defaults to 1.',
        'react_<type>': 'Reacts to the most recent message in this channel with emoji of chosen [type].',
        'NEWadd_<type>': 'Adds the linked image as an emoji of [type] (must attach image to this message to work)',
        'NEWlist': 'Displays a list of emoji [type]s known to Emojibot'
    }
    #Sets up the help menu as a fancy embed for formatting
    help_body_text = "" # Start with a blank block of text and build up
    for key in commands_dict: #Display commands (special icons for newly added ones)
        if key[:3] == "NEW":
            help_body_text += help_new_emoji+" **e!"+key[3:].replace('_',' ')+"**\n"
            help_body_text += commands_dict[key]+"\n\n"
        else:
            help_body_text += help_diamond_emoji+" **e!"+key.replace('_',' ')+"**\n"
            help_body_text += commands_dict[key]+"\n\n"
    # Build and send the "embed" that contains the above information
    embed=discord.Embed(title="",description=help_body_text,color=help_color)
    embed.set_author(name="Help Menu", icon_url=help_icon)
    await ctx.send(embed=embed)

    gc.collect() # collect garbage
    return

# Send command: Sends [quantity] of [type] emoji
@bot.command(name='send',ignore_extra=False)
async def emoji_send(ctx,type,quantity='1'): #Default quantity to 1
    # Set up some thresholds
    emoji_thresh = 54 # 2 lines worth of emojis, discord's max per message is higher but this is neater
    max_emojis = 999 # Limits the spamming of emojis by bad actors

    await ctx.message.delete() # Deletes the user's command for streamlined visuals

    # Reads the emoji_list.json file to see the available emojis
    with open(json_path,'r') as file:
        emoji_dict = json.load(file)
    #print('test')
    if quantity.isdigit(): # Need a number for quantity
        #print(int(quantity))
        if int(quantity) > 0: # Number has to be positive
            #print("think")
            num_emoji = int(quantity)
            if num_emoji > max_emojis: # Number has to be less than spam threshold
                await ctx.send("That's too many")
                gc.collect() # garbage collect
                return
        else:
            await ctx.send("Quantity needs to be a POSITIVE number")
            gc.collect() # garbage collect
            return
    else:
        await ctx.send("Quantity needs to be a number")
        gc.collect() # garbage collect
        return
    #print('wut')
    # In the case of large numbers of emojis it needs to be broken into many messages
    while num_emoji > emoji_thresh: # Send messages untill all that's left fits in one message
        if type.lower() in emoji_dict: # Checks the emoji to confirm the bot knows it
            await ctx.send(emoji_dict[type.lower()]*emoji_thresh)
        else: # If it doesn't then tell the user what they sent
            await ctx.send("I don't have **%s** yet, but maybe you can add it?" % type.lower())
            gc.collect() # garbage collect
            return
        num_emoji = num_emoji - emoji_thresh # accounts for how many are left to send
    # Sends remaining number of emokis
    if type.lower() in emoji_dict:  # Checks the emoji to confirm the bot knows it
        await ctx.send(emoji_dict[type.lower()]*num_emoji)
    else: # If it doesn't then tell the user what they sent
        await ctx.send("I don't have **%s** yet, but maybe you can add it?" % type.lower())
        gc.collect() # garbage collect
        return
    gc.collect() # garbage collect
    return

# React command: reacts to most recent message in this channel with [type] emoji
@bot.command(name='react',ignore_extra=False)
async def emoji_react(ctx,type):
    #print('hoi')
    #print(ctx.channel.last_message_id)
    await ctx.message.delete() # Deletes the user's command for streamlined visuals
    # Reads the emoji_list.json file to see the available emojis
    with open(json_path,'r') as file:
        emoji_dict = json.load(file)
    #print(ctx.channel.last_message_id)
    async for message in ctx.channel.history(limit=1): # Grab the ID of the most recent message
        nab = message.id
    message = await ctx.fetch_message(nab) # Grab the actual message from the ID
    #print(message)
    #print('test')
    if type.lower() in emoji_dict:   # Checks the emoji to confirm the bot knows it
        await message.add_reaction(emoji_dict[type.lower()]) # add reaction
    else: # If it doesn't then tell the user what they sent
        await ctx.send("I don't have **%s** yet, but maybe you can add it?" % type.lower())
        gc.collect() # garbage collect
        return
    gc.collect() # garbage collect
    return

# Add command: Adds [type] emoji from attached image
@bot.command(name='add',ignore_extra=False)
async def emoji_add(ctx,type):
    # Set up some local variables
    end_size = 128 # Largest dimension allowed in discord emoji
    max_bytes = 5000000 # File size limit in bytes (arbitrary but necessary)
    image_path = type.lower()+".png" # sets up relative filepath to temporarily store the image

    await ctx.message.delete() # Deletes the user's command for streamlined visuals

    if not type == re.escape(type): # check the name for special characters, python thinks they're regex
        await ctx.send("The name cannot contain special characters, sorry :(")
        gc.collect() # garbage collect
        return
    message = ctx.message #grab message once for ease of use

    # Reads the emoji_list.json file to see the available emojis
    with open(json_path,'r') as file:
        emoji_dict = json.load(file)

    # Check to see if the new emoji CAN be added
    if len(emoji_dict) >= 50: # If the bot's backup server is full, can't add another one
        await ctx.send("I already have too many emojis. See **e!list** for what is available and ask the dev for help if you still want to add something.")
        gc.collect() # garbage collect
        return
    if type.lower() in emoji_dict: # If the name is already in use, can't add another one
        await ctx.send("I already have an emoji of type **%s**. See **e!list** for details and/or name your emoji something else." % type.lower())
        gc.collect()
        return
    if len(message.attachments) < 1: # Ensure there was an actual image attached
        await ctx.send("You need to actually attach an image to the message to add it as an emoji.")
        gc.collect()
        return

    #print(message.attachments[0].url,message.attachments[0].size)
    if(message.attachments[0].size > max_bytes): # Check that the image is small enough to save/use
        await ctx.send("The image you gave me is too big; please make a smaller version and try again!")
        gc.collect()
        return
    # Save the attached image at the local filepath
    with open(image_path,'wb') as file:
        await message.attachments[0].save(file)
    # Use Pillow to open this image and re-size it while preserving alpha channel
    image = pillow.open(image_path) #open the image
    [x,y] = image.size # get current size
    if x > end_size or y > end_size: # If the image is too big
        if x > y: # set the "scale" by the larger dimension
            scale = end_size/x
        else:
            scale = end_size/y
        # resize by scale to keep image fidelity in tact
        width = int(x * scale)
        height = int(y * scale)
        size = (width,height)
        image = image.resize(size) #store this in the same variable
        image.save(image_path) #save this at the relative path

    # Now no matter what the file at the relative path is at the right dimensions
    with open(image_path, 'rb') as file: # open this as a binary file (needs for discord)
        resized = file.read()

    # Actually add the emoji to the backup server with [type] as its name
    tmp = await bot.guilds[guild_index].create_custom_emoji(name = type.lower(),image = resized)
    #print(str(tmp))
    emoji_dict[type.lower()] = str(tmp) # Add the full ID for this emoji to the dictionary
    # Write the updated dictionary to the json file
    with open(json_path,'w') as file:
        json.dump(emoji_dict,file)

    os.remove(image_path) # Delete the locally stored image

    # Send some output to the user so the user knows the command executed properly
    await ctx.send("I have successfully added **%s** to my list of emotes!" % type.lower())
    await ctx.send(emoji_dict[type.lower()]) # and so they can see how the emoji looks
    gc.collect() # garbage collection
    return

# List command: Lists all the known emojis to emojibot
@bot.command(name='list',ignore_extra=True)
async def emoji_list(ctx):
    await ctx.message.delete() # Deletes the user's command for streamlined visuals

    # Reads the emoji_list.json file to see the available emojis
    with open(json_path,'r') as file:
        emoji_dict = json.load(file)

    #Sets up the emoji list as a fancy embed for formatting
    list_body_text = "" # Start with a blank block of text and build up
    for key in emoji_dict: #iterate through dictionary and list the emotes
        list_body_text += key+": "+emoji_dict[key]+"\n"

    # Build and send the "embed" that contains the above information
    embed=discord.Embed(title="",description=list_body_text,color=help_color)
    embed.set_author(name="List of Emojis", icon_url=help_icon)
    await ctx.send(embed=embed)

    gc.collect() # garbage collection
    return

# Delete command: Deletes [type] emoji from list (Dev command not in help menu)
@bot.command(name='delete',ignore_extra=True)
async def emoji_delete(ctx,type):
    await ctx.message.delete() # Deletes the user's command for streamlined visuals
    #print(ctx.message.author.id, DEV_ID)
    if not ctx.message.author.id == DEV_ID: # Checks user's ID against Dev's ID
        await ctx.send("You don't have permission to do that, silly.")
    else: # If the Dev used the command
        # Reads the emoji_list.json file to see the available emojis
        with open(json_path,'r') as file:
            emoji_dict = json.load(file)

        if type.lower() in emoji_dict: # Ensures the specified emoji exists
            del emoji_dict[type.lower()] # Deletes the entry from the dictionary
            # Write the updated dictionary to the json file
            with open(json_path,'w') as file:
                json.dump(emoji_dict,file)

            # DM's the Dev so they don't forget to remove the emoji from the backup server
            dev_user = await bot.fetch_user(DEV_ID)
            await dev_user.create_dm()
            await dev_user.dm_channel.send("You have to remove **%s** emoji" % type.lower())
        else:
            await ctx.send("Can't delete what I don't have.")
    gc.collect() # garbage collection
    return

# ERROR EVENTS (COMMAND NOT FOUND, MISSING ARGUMENT, MISSING ROLE, OTHER)
@bot.event
async def on_command_error(ctx, error): #Handles any command errors
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument): #Missing an argument
        await ctx.send("You need to include more arguments. See **e!help** for details.")
    else:
        await ctx.send("I encountered a problem, but I've alerted the Dev to debug it.")
        # DM's the Dev so they can see the error
        dev_user = await bot.fetch_user(DEV_ID)
        await dev_user.create_dm()
        await dev_user.dm_channel.send(error)
    gc.collect() # garbage collection
    return

## END OF BOT FUNCTIONS

bot.run(TOKEN) # runs the bot
