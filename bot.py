from slugify import slugify
from gtts import gTTS
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
from discord.ext.commands.errors import CheckFailure, CommandInvokeError, MissingRequiredArgument
import asyncio
import urllib.parse
from discord.errors import ClientException
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='!')
dictionary = PyDictionary()
now = datetime.datetime.now()


categories = {"9": "General Knowledge", "10": "Entertainment: Books", "11": "Entertainment: Film", "12": "Entertainment: Music",
              "13": "Entertainment: Musicals & Theatres", "14": "Entertainment: Television", "15": "Entertainment: Video Games",
              "16": "Entertainment: Board Games", "17": "Science & Nature", "18": "Science: Computers", "19": "Science: Mathematics",
              "20": "Mythology", "21": "Sports", "22": "Geography", "23": "History", "24": "Politics", "25": "Art",
              "26": "Celebrities", "27": "Animals", "28": "Vehicles", "29": "Entertainment: Comics", "30": "Science: Gadgets",
              "31": "Entertainment: Japanese Anime & Manga", "32": "Entertainment: Cartoon & Animations"}


@loop(hours=1)
async def batch_update():
    if (now.hour == 9):
        await sendMessage()


async def sendMessage():
    channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
    for nmb in range(0, 5):
        ind = random.randint(0, 5995)
        response = "``` ** START OF THE WORD ** ```" + getMeaning(allwords.words[ind]) + getAntonyms(allwords.words[ind]) + "\n" + getSynonyms(allwords.words[ind]) + "``` ** END OF THE WORD ** ```"
        await channel.send(response)
        time.sleep(10)


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
    response = \
        "**Usage**\n" +\
        "**!maneng**    Show usage.\n" +\
        "**!define <word>**    Get information about the word.\n" +\
        "**!say <word>||<sentence>**    Say the given input.\n" +\
        "**!ant <word>**    Get antonyms of the word.\n" +\
        "**!syn <word>**    Get synonyms of the word.\n" +\
        "**!exm <word>**    Get an example sentence about the word.\n" +\
        "**!play**    Play a game. \n" +\
        f"**!comp <number>** Start a competition with given number of questions. (Default is 30)\n" +\
        "**!tte <word>||<sentence>** Convert given input to emoji :-D"
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


def getQuestion(category_number=18):
    url = f"https://opentdb.com/api.php?amount=10&category={category_number}&type=multiple&encode=url3986"
    toparse = requests.request("GET", url)
    if toparse.json()["response_code"] != 0:
        return None
    q = random.choice((toparse.json()['results']))
    answers = {"A": "", "B": "", "C": "", "D": ""}
    question = {"question": urllib.parse.unquote(q["question"]), "difficulty": q["difficulty"]}
    answerOption = random.choice(list(answers.keys()))
    index = 0
    for key, value in answers.items():
        if answerOption == key:
            question[key] = urllib.parse.unquote(q["correct_answer"])
            question['answer'] = key
        else:
            question[key] = urllib.parse.unquote(q["incorrect_answers"][index])
            index += 1
    return question


# Play Game helper functions
is_game_running = None


def stopGame():
    global is_game_running
    is_game_running = False


def startGame():
    global is_game_running
    is_game_running = True


def incrementUserPoint(user, difficulty):
    global user_points
    point = 0
    if difficulty == "easy":
        point = 10
    elif difficulty == "medium":
        point = 20
    elif difficulty == "hard":
        point = 30
    if user in user_points.keys():
        user_points[user] += point
    else:
        user_points[user] = point


async def play_game(ctx, *args):
    if is_game_running:
        return
    startGame()
    delay = 15.0
    channel = ctx.channel
    emojies = {"A": '🇦', "B": '🇧', "C": '🇨', "D": '🇩'}
    category_number = random.choices(list(range(9, 33)), list([.5/23]*9+[.5]+[.5/23]*14))[0]  # this will distrubute probability so that the number 18 has %50 chance.
    question = getQuestion(category_number)
    if not question:
        stopGame()
        return
    questionString = ""
    if is_competition_running:
        questionString += f"```Question {current_question}/{number_of_questions}, " +\
            f"Category: {categories[str(category_number)]}```"
    else:
        questionString += f"Category: **{categories[str(category_number)]}**\n"
    questionString += \
        f"{question['question']}\n" +\
        f"**Choose correct answer, you have {delay} seconds to answer**\n" +\
        f"> {emojies['A']}   {question['A']}\n" +\
        f"> {emojies['B']}   {question['B']}\n" +\
        f"> {emojies['C']}   {question['C']}\n" +\
        f"> {emojies['D']}   {question['D']}\n\n"

    message = await channel.send(questionString)
    answer_emoji = ""
    for key, emo in emojies.items():
        await message.add_reaction(emo)
        if question["answer"] == key:
            answer_emoji = emo

    def check(reaction, user):  # dummy check function
        return False
    reaction = None
    users_correct = []
    users_uncorrect = []
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=delay, check=check)
    except asyncio.TimeoutError:
        try:
            msg = await channel.fetch_message(message.id)
        except:
            await ctx.send(f"Hey admins!! Please don't delete messages! \nI don't give u correct answer, huff huff huff 👿!! ")
            stopGame()
            return
        reaction = None
        i = 0
        for ans in ["A", "B", "C", "D"]:
            try:
                reaction = msg.reactions[i]
                if reaction.emoji not in emojies.values():
                    await ctx.send(f"Please don't send custom emojies, otherwise we will find you! \nI don't give u correct answer, huff huff huff 👿!! ")
                    stopGame()
                    return
            except:
                await ctx.send(f"Please don't send custom emojies, otherwise we will find you! \nI don't give u correct answer, huff huff huff 👿!! ")
                stopGame()
                return
            i += 1
            async for user in reaction.users():
                if user.id != client.user.id:
                    if question["answer"] == ans:
                        users_correct.append(user.name)
                    else:
                        users_uncorrect.append(user.name)
    for user in users_uncorrect:
        if user in users_correct:
            users_correct.remove(user)
    if is_game_running:
        if len(users_correct) > 0:
            await ctx.send(f"Correct answer is {answer_emoji}\n**Users who get correct answer are**")
            await ctx.send(', '.join(users_correct))
            if is_competition_running:
                for user in users_correct:
                    incrementUserPoint(user, question["difficulty"])
        else:
            await ctx.send(f"**Opps! Nobody answers correctly**\nCorrect answer is **{answer_emoji}**")
        stopGame()

# Competition helper functions
number_of_questions = 30
current_question = 1
is_competition_running = False
comp_ctx = None
user_points = {}


def initCompetition(ctx, args):
    global comp_ctx, number_of_questions, is_competition_running
    if len(args) != 0 and len(args) > 1:  # if user enter too many arguments
        return "Too many argument!!"
    elif len(args) == 1:  # user enters exactly 1 argument.
        try:
            n = int(args[0])
            if not n > 0:
                return "Number must be greater than 0."
            elif not n <=30:
                return "Number must be less than 30."
            number_of_questions = int(args[0])
        except ValueError:
            return "Please enter a number!!"
        except Exception as e:
            return f"Unknown error \n{e}"
    else:
        pass  # The argument numbers are proper
    comp_ctx = ctx
    is_competition_running = True
    return "ok"


def resetCompetition():
    global current_question, is_game_running, user_points, number_of_questions, is_competition_running, comp_ctx
    user_points = {}
    stopGame()
    current_question = 1
    is_competition_running = False
    comp_ctx = False
    number_of_questions = 30


def incrementQuestionNumber():
    global current_question
    current_question += 1


@loop(seconds=20)
async def competitionLoop():
    channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
    await play_game(comp_ctx)
    incrementQuestionNumber()
    if current_question > number_of_questions:
        user_points_temp = sorted(user_points, key=user_points.get, reverse=True)
        await channel.send("```Competition is finished!```Here the **winner**s are:\n")
        response = []
        for user in user_points_temp:
            response.append(f"{user}:**{user_points[user]}**")
        if len(response) == 0:
            await channel.send("||¯\_(ツ)_/¯||")
        else:
            await channel.send("||"+('\n'.join(response))+"||")
        resetCompetition()
        competitionLoop.stop()
# TTE helper functions


def charToEmoji(ch):
    ch = ch.lower()
    if slugify(ch) and slugify(ch) != ch:  # if char not in english alphabet
        ch = slugify(ch)
    numStr = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    if '0' <= ch <= '9':
        offset = ord(ch)-ord('0')  # exm : (ascii value of '1') -(ascii value of '0')==1
        return ":" + numStr[offset] + ":"
    if 'a' <= ch <= 'z':
        return ":regional_indicator_" + ch.lower() + ":"
    special_chars = {
        "?": ":grey_question:",
        "!": ":grey_exclamation:",
        ".": ":record_button:"
    }
    if ch in special_chars.keys():
        return special_chars[ch]


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


@client.command(name="play")
async def start_game(ctx, *args):
    try:
        await play_game(ctx, *args)
    except:
        await ctx.send("**OPPS!! 404 NOT FOUND!")
        stopGame()


@client.command(name="comp")
async def start_competition(ctx, *args):
    if not is_competition_running:
        response = initCompetition(ctx, args)
        if response == "ok":
            try:
                competitionLoop.start()
            except Exception as e:
                await ctx.send(f"Unknown error {e}")
                return
        else:
            await ctx.send(response)


@client.command(name="compstop")
async def stop_competition(ctx, *args):
    for role in [x.lower() for x in eval(os.getenv("ADMIN_ROLES"))]:
        if role in [y.name.lower() for y in ctx.author.roles]:
            await ctx.send(f"Competition has ended by {ctx.author.name}")
            competitionLoop.stop()
            break


@client.command(name="say")
async def text_to_voice(ctx, *, arg):
    filename = slugify(arg)+".mp3"
    sp = gTTS(text=arg, lang="en", slow=False)
    sp.save(filename)
    await ctx.send(file=discord.File(filename))
    os.remove(filename)


@client.command(name="tte")
async def text_to_emoji(ctx, *args):
    response = ""
    if len(args) == 0:
        raise IndexError  # user not entered any word
    for arg in args:
        emojitified = ""
        for ch in arg:
            converted = charToEmoji(ch)
            if converted:  # if char is converted
                emojitified += " " + converted
        response += " " + emojitified+"     "
    if len(response.strip()) == 0:  # if all of the chars are not converted
        await ctx.send("Unknown char at line 1!! Segmentation Fault..")
        return
    await ctx.send(response)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):  # if user enter an unused command do nothing
        return
    elif isinstance(error, CheckFailure):  # if global check fail do nothing
        return
    elif isinstance(error, MissingRequiredArgument) or isinstance(error.original, IndexError):  # if command function raise IndexError which mean command send with no word
        await ctx.send("You forgot to enter a word!")
        return
    stopGame()
    raise error


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord")
    batch_update.start()

client.run(TOKEN)
