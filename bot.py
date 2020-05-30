import os
import discord
from nltk.corpus import wordnet
from PyDictionary import PyDictionary
from dotenv import load_dotenv
import random
import allwords
import time
from discord.ext import tasks
import datetime
import requests
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
dictionary = PyDictionary()

now = datetime.datetime.now()


@tasks.loop(hours =1.0)
async def batch_update():
    if (now.hour == 9):
        await sendMessage()


async def sendMessage():
    channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
    for nmb in range(0,5):
        ind = random.randint(0,5995)
        response ="``` ```"
        response += getMeaning(allwords.words[ind])
        response += getAntonyms(allwords.words[ind])
        response += getSynonyms(allwords.words[ind])
        await channel.send(response)
        time.sleep(6)

def getMeaning(word):
    #get definition
    definition = dictionary.meaning(word) #returns a dictionary in the form {'Part of Speech': ['definition(s)']}

    #getting the parts of speech in a list

    parts_of_speech = []
    response=""
    try:
        parts_of_speech = list(definition.keys())
        defNum = 0

        for i in parts_of_speech:
            #state the part of speech
            response += i + ": \n"
            #Loop through each definition per part of speech
            for defin in definition[i]:
                #make it so we don't output a bunch of definitions/spam chat
                defNum += 1
                if(defNum <= 3):
                    #Tack on another definition plus a \n
                    response += defin + "\n"
                else:
                    break
            #Space the parts of speech accordingly
            defNum = 0
            #definition[i] is an array of definitions, so what we want to do is loop through each definition[i] and print out those definitions
    except:
        response = ""

    if (response.strip()==""):
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
                ant.append(lemma.antonyms()[0].name()) #add the synonyms to syn

    ant = set(ant) #use a set to get rid of duplicates

    if(word in ant): #a word being its own antonym is redundant
        ant.remove(word)

    for antonym in ant:
        antNum += 1
        if(antNum <= 5):
            #Tack on another synonym plus a \n
            response += antonym + "\n"
        else:
            break

    if (response.strip()==""):
        response = "\nWe couldn't find antonyms of that word!"
        return response
    else:
        response="\n**Antonyms of " + words + "**\n"+response
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
            syn.append(word) #add the synonyms to syn

    syn = set(syn) #use a set to get rid of duplicates

    if(word in syn): #a word being its own synonym is redundant
        syn.remove(word)

    for synonym in syn:
        synNum += 1
        if(synNum <= 5):
            #Tack on another synonym plus a \n
            response += synonym + "\n"
        else:
            break

    if (response.strip()==""):
        return "\nWe couldn't find synonyms of that word!"
    else:
        return "\n**Synonyms of " + word + "**\n"+response

def getUsage():
    response="""\
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

    response = requests.request("GET", url, headers=headers)
    return random.choice(response.json()['examples'])


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if (message.channel.id!=int(os.getenv("CHAT_CHANNEL"))):
        return

    #print("Gelen Kanal",message.channel.id)
    msg = message.content
    response = ""
    commands = msg.split(" ")
    if message.content.startswith('!maneng'):
        response = getUsage()
        await message.channel.send(response)
        return
    try:
        word = commands[1]
        print(word)
    except:
        response = "You forgot to enter a word!"
        await message.channel.send(response)
        pass

    if word.lower()=="mdisec":
        response = "**Congratz!! You get secret word of life.** \n**MDISEC** \nThe community of greatness "
        await message.channel.send(response)
        return

    if message.content.startswith('!define'):
        response = getMeaning(word)
        await message.channel.send(response)

    elif message.content.startswith("!syn"):
        response = getSynonyms(word)
        await message.channel.send(response)

    elif message.content.startswith("!ant"):
        response = getAntonyms(word)
        await message.channel.send(response)

    elif message.content.startswith("!exm"):
        response = getExampleSentence(word)
        await message.channel.send(response)

@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord")
    batch_update.start()

client.run(TOKEN)
