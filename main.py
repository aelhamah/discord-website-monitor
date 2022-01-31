# Importing libraries
from bs4 import BeautifulSoup
import discord
import hashlib
from markdownify import markdownify
import os
import random
import time
from urllib.request import urlopen, Request
import requests


client = discord.Client()

# monitor eecs280.org for changes
url = Request('https://eecs280staff.github.io/eecs280.org/', headers={'User-Agent': 'Mozilla/5.0'})

@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)

    response = urlopen(url).read()
    soup = BeautifulSoup(response, 'html.parser')
    html = soup.find('div', id='announcements')
    current_hash = hashlib.sha224(str(html).encode('utf-8')).hexdigest()
    while True:
      try:
        time.sleep(60)
        print("checking ... time:" + time.asctime(time.localtime()))

        # get the new hash 
        response = urlopen(url).read()
        soup = BeautifulSoup(response, 'html.parser')
        html = soup.find('div', id='announcements')
        new_hash = hashlib.sha224(str(html).encode('utf-8')).hexdigest()

        if current_hash != new_hash:
          print("something changed")
          await send_message(html)
          current_hash = new_hash

      except Exception as e:
        print("logging error ... ")
        requests.post(os.environ['LOG_URL'], json={'message': str(e)})


async def send_message(html):
  # begin the embedded message
  embedVars = []
  for child in html.contents:
    if not isinstance(child, str):
      if child.has_attr('class'):
        if 'header' in child['class']:
          # begin the embedded message
          embedVars.append(discord.Embed(title=child.text.strip('\n').strip(), description="", color=int(random.random()*16777215)))
        else:
          embedVars[-1].description += markdownify(str(child))
      else:
          embedVars[-1].description += markdownify(str(child))
    
  # send the message
  channel = client.get_channel(os.environ['CHANNEL_ID'])
  if len(embedVars) > 0:
    # mention the remind role
    await channel.send("<@&{}>\n".format(os.environ['ROLE_ID']))
  for embedVar in embedVars:
    time.sleep(1)
    await channel.send(embed=embedVar)    

client.run(os.environ['TOKEN'])
