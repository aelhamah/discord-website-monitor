# Importing libraries
import discord
import os
from bs4 import BeautifulSoup
import hashlib
from markdownify import markdownify
import time
from urllib.request import urlopen, Request

client = discord.Client()

# monitor eecs280.org for changes
url = Request('https://eecs280staff.github.io/eecs280.org/',
        headers={'User-Agent': 'Mozilla/5.0'})

@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)

    response = urlopen(url).read()
    soup = BeautifulSoup(response, 'html.parser')
    html = soup.find('div', id='announcements')
    current_hash = hashlib.sha224(str(html).encode('utf-8')).hexdigest()
    while True:
      time.sleep(10)
      print("checking")

      # get the new hash 
      response = urlopen(url).read()
      soup = BeautifulSoup(response, 'html.parser')
      html = soup.find('div', id='announcements')
      new_hash = hashlib.sha224(str(html).encode('utf-8')).hexdigest()

      if current_hash != new_hash:
        print("something changed")
        await send_message(html)
        current_hash = new_hash


async def send_message(html):
  # begin the embedded message
  embedVar = discord.Embed(title="Course Updates", description="", color=0xE62C2D)

  # parse the announcements
  fields = []
  for child in html.contents:
    if not isinstance(child, str):
      if child.has_attr('class'):
        if 'header' in child['class']:
            fields.append({
                "title": child.text.strip('\n').strip(),
                "description": "",
            })
        else:
          fields[-1]["description"] += markdownify(str(child))
      else:
          fields[-1]["description"] += markdownify(str(child))
  
  for item in fields:
    embedVar.add_field(name=item["title"], value=item["description"], inline=False) 
    
  # send the message
  channel = client.get_channel(928080755987456010)
  await channel.send("@remind \n", embed=embedVar)  

client.run(os.environ['TOKEN'])
