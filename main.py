"""Discord bot checks for new messages and sends them to the channel."""
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

# keeps track of previous elements
elements = []

# get discord client
client = discord.Client()

# monitor eecs280.org for changes
url = Request(
    "https://eecs280staff.github.io/eecs280.org/", headers={"User-Agent": "Mozilla/5.0"}
)


@client.event
async def on_ready():
    """When the bot is ready, print the bot's name and ID."""
    print("Logged in as " + client.user.name)

    # Initizalize the elements
    response = urlopen(url).read()
    soup = BeautifulSoup(response, "html.parser")
    html = soup.select(".ui.message.info")
    # hash each element in html and add it to elements
    for element in html:
        elements.append(hashlib.sha224(str(element).encode("utf-8")).hexdigest())

    while True:
        try:
            time.sleep(60)
            print("checking ... time:" + time.asctime(time.localtime()))

            # get the new hash
            response = urlopen(url).read()
            soup = BeautifulSoup(response, "html.parser")
            html = soup.select(".ui.message.info")
            for element in html:
                new_hash = hashlib.sha224(str(element).encode("utf-8")).hexdigest()
                if new_hash not in elements:
                    print("something changed")
                    await send_message(element)
                    elements.append(new_hash)
                    if len(elements) > 8:
                        elements.pop(0)

        except Exception as e:
            print("logging error ... ")
            requests.post(os.environ["LOG_URL"], json={"message": str(e)})


def reparse_for_internal_links(embedvar):
    """Replace internal links with markdown links."""
    desc = embedvar.description.split(" ")
    for i, _ in enumerate(desc):
        # search for markdown links using re where anyt
        if "](#" in desc[i]:
            # add https://eecs280staff.github.io/eecs280.org/ to the link
            desc[i] = desc[i].replace(
                "](#", "](https://eecs280staff.github.io/eecs280.org/#"
            )
    embedvar.description = " ".join(desc)


async def send_message(html):
    """Send the message to the channel."""
    # begin the embedded message
    embedVars = []
    for child in html.contents:
        if not isinstance(child, str):
            if child.has_attr("class"):
                if "header" in child["class"]:
                    # begin the embedded message
                    embedVars.append(
                        discord.Embed(
                            title=child.text.strip("\n").strip(),
                            description="",
                            color=int(random.random() * 16777215),
                        )
                    )
                else:
                    embedVars[-1].description += markdownify(str(child))
            else:
                embedVars[-1].description += markdownify(str(child))

    # send the message
    channel = client.get_channel(int(os.environ["CHANNEL_ID"]))
    if len(embedVars) > 0:
        # mention the remind role
        await channel.send(
            embed=discord.Embed(
                description="<@&{}> updates to [eecs280.org](https://eecs280.org):".format(
                    os.environ["ROLE_ID"]
                ),
            )
        )
    for embedVar in embedVars:
        time.sleep(1)
        reparse_for_internal_links(embedVar)
        await channel.send(embed=embedVar)


client.run(os.environ["TOKEN"])
