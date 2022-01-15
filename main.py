# Importing libraries
import discord
import os
from bs4 import BeautifulSoup
import hashlib
from keep_alive import keep_alive
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

    while True:
      try:
        print('Checking')

        # get the current state of announcements
        response = urlopen(url).read()
        soup = BeautifulSoup(response, 'html.parser')
        html = soup.find('div', id='announcements')
        currentHash = hashlib.sha224(str(html).encode('utf-8')).hexdigest()
        
        # wait 
        time.sleep(10)
        
        # get the current state of announcements
        response = urlopen(url).read()
        soup = BeautifulSoup(response, 'html.parser')
        html = soup.find('div', id='announcements')
        newHash = hashlib.sha224(str(html).encode('utf-8')).hexdigest()

        # check if new hash is same as the previous hash
        if newHash == currentHash:
          continue

        # if something changed in the hashes
        else:
          # notify
          print("something changed")

          # reset the current hash
          currentHash = newHash
          
		      # begin the embedded message
          embedVar = embedVar = discord.Embed(title="Course Updates", description="", color=0xE62C2D)

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
          
		  # wait
          time.sleep(10)
          continue
          
      # To handle exceptions
      except Exception as e:
        print(e)
        print("error")

keep_alive()
client.run(os.environ['TOKEN'])

