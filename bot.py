import os
import discord
from nltk.corpus import wordnet
from PyDictionary import PyDictionary
from dotenv import load_dotenv
import random
import allwords
import time
from discord.ext.tasks import loop
import datetime
import requests
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord.ext.commands.errors import CheckFailure, CommandInvokeError
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='!')

dictionary = PyDictionary()
now = datetime.datetime.now()


@loop(hours=1)
async def batch_update():
    if (now.hour == 14):
        await sendMessage()

async def sendMessage():
    channel = client.get_channel(int(os.getenv('CHAT_CHANNEL')))
    for nmb in range(0,5):
        ind = random.randint(0,5995)
        response ="``` ** START OF THE WORD ** ```" + getMeaning(allwords.words[ind]) + getAntonyms(allwords.words[ind]) + "\n" + getSynonyms(allwords.words[ind]) + "``` ** END OF THE WORD ** ```"
        await channel.send(response)
        time.sleep(3)


def getMeaning(word):
    # get definition
    definition = dictionary.meaning(word)  # returns a dictionary in the form {'Part of Speech': ['definition(s)']}

    # getting the parts of speech in a list

    parts_of_speech = []
    response = ""
    try:
        parts_of_speech = list(definition.keys())
        defNum = 0

        for i in parts_of_speech:
            # state the part of speech
            response += i + ": \n"
            # Loop through each definition per part of speech
            for defin in definition[i]:
                # make it so we don't output a bunch of definitions/spam chat
                defNum += 1
                if(defNum <= 3):
                    # Tack on another definition plus a \n
                    response += defin + "\n"
                else:
                    break
            # Space the parts of speech accordingly
            defNum = 0
            # definition[i] is an array of definitions, so what we want to do is loop through each definition[i] and print out those definitions
    except:
        response = ""

    if (response.strip() == ""):
        return "Sorry! For some reason we can't find this definition."
    else:
        return "**"+word+"** \n"+response


def getAntonyms(words):
    response = ""
    ant = []
    antNum = 0
    for ss in wordnet.synsets(words):
        for lemma in ss.lemmas():
            word = lemma.name()
            if('_' in lemma.name()):
                word = word.replace('_', " ")

            if lemma.antonyms():
                ant.append(lemma.antonyms()[0].name())  # add the synonyms to syn

    ant = set(ant)  # use a set to get rid of duplicates

    if(word in ant):  # a word being its own antonym is redundant
        ant.remove(word)

    for antonym in ant:
        antNum += 1
        if(antNum <= 5):
            # Tack on another synonym plus a \n
            response += antonym + "\n"
        else:
            break

    if (response.strip() == ""):
        response = "\nWe couldn't find antonyms of that word!"
        return response
    else:
        response = "\n**Antonyms of " + word + "**\n"+response
        return response


def getSynonyms(word):
    response = ""
    syn = []
    synNum = 0
    for ss in wordnet.synsets(word):
        for lemma in ss.lemmas():
            word = lemma.name()
            if('_' in lemma.name()):
                word = word.replace('_', " ")
            syn.append(word)  # add the synonyms to syn

    syn = set(syn)  # use a set to get rid of duplicates

    if(word in syn):  # a word being its own synonym is redundant
        syn.remove(word)

    for synonym in syn:
        synNum += 1
        if(synNum <= 5):
            # Tack on another synonym plus a \n
            response += synonym + "\n"
        else:
            break

    if (response.strip() == ""):
        return "\nWe couldn't find synonyms of that word!"
    else:
        return "\n**Synonyms of " + word + "**\n"+response


def getUsage():
    response = """\
**Usage**
**!maneng**    Show usage.
**!define <word>**    Get information about the word.
**!ant <word>**    Get antonyms of the word.
**!syn <word>**    Get synonyms of the word.
**!exm <word>**    Get an example sentence about the word."""
    return response


def getExampleSentence(word):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/examples"
    headers = {
        'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
        'x-rapidapi-key': f"{os.getenv('WORDS_API_KEY')}"
    }

    toparse = requests.request("GET", url, headers=headers)
    response = "**The example contains  *" + word + "*  is** \n" + random.choice(toparse.json()['examples'])
    return response


@client.check  # global checks for all commands
async def globally_block_dms(ctx):
    return ctx.channel.id == int(os.getenv("CHAT_CHANNEL"))


@client.command(name="maneng")
async def show_usage(ctx, *args):
    await ctx.send(getUsage())


@client.command(name="define")
async def sendMeaning(ctx, *args):
    word = args[0]
    await ctx.send(getMeaning(word))


@client.command(name="syn")
async def sendSynonyms(ctx, *args):
    word = args[0]
    await ctx.send(getSynonyms(word))


@client.command(name="ant")
async def sendAntonyms(ctx, *args):
    word = args[0]
    await ctx.send(getAntonyms(word))


@client.command(name="exm")
async def sendExampleSentence(ctx, *args):
    word = args[0]
    await ctx.send(getExampleSentence(word))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):  # if user enter an unused command do nothing
        return
    elif isinstance(error, CheckFailure):  # if global check fail do nothing
        return
    elif isinstance(error.original, IndexError):  # if command function raise IndexError which mean command send with no word
        await ctx.send("You forgot to enter a word!")
        return
    raise error


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord")
    batch_update.start()

client.run(TOKEN)
