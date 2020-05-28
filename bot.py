#!/bin/python3

import os
import discord
import asyncio
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import allwords


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()


url = 'https://translate.google.com/'
postreq = requests.get(url, data={'tl':'tr', "client":'webapp','sl':'en', 'q': allwords.words[5]})
print(postreq)



#soup = BeautifulSoup(page.content, 'html.parser')
#results = soup.findAll("div", {"class": "word-and-pronunciation"})

#print(allwords.words[5995])

#@client.event  
#async def on_message(message):
#    if message.author == client.user:
#        return
#
#    if message.content.startswith('!5kelime'):
        #msg = 'Todays words are: '.format(message)
#    	await message.channel.send('I heard you! {}'.format(message))
#        
#
#@client.event
#async def on_ready():
#	print(f"{client.user} has connected to Discord")
#	
#client.run(TOKEN)
