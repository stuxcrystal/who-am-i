#!/usr/bin/env python3
import dotenv
dotenv.load_dotenv()

import os
import random
import logging
import pathlib
import asyncio

import uvloop
import discord

logging.basicConfig(format="[%(levelname)s] %(message)s", level=getattr(logging, os.environ["LOGGING_LEVEL"]))
uvloop.install()

import static_config


DISCORD_CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
DISCORD_CLIENT_SECRET = os.environ["DISCORD_CLIENT_SECRET"]
DISCORD_CLIENT_TOKEN = os.environ["DISCORD_CLIENT_TOKEN"]


class Bot:

    def run(self):
        logging.info("Booting up...")
        client = discord.Client()
        client.event(self.on_message)

        logging.info("Starting...")
        client.run(DISCORD_CLIENT_TOKEN)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.content.startswith("i-am! "):
            return

        content = message.content
        content = content[6:]
        if " " not in content:
            await message.channel.send("""__Usage:__
**i-am! [Name] [Subject-Pronoun]**
**i-am! [Name] [Subject-Pronoun]/[Object-Pronoun]**
Example: `i-am! Sarah she` / `i-am! Roland he/him`

**i-am! [Name] [Subject-Pronoun]/[Object-Pronoun]/[Possessive-Determiner]/[Possessive-Pronoun]/[Reflexive] **
Example: `i-am! Laura she` 
""")
            return

        name, pronoun_list = content.split(" ", 2)
        pronouns = pronoun_list.lower().split("/")
        if len(pronouns) < 5:
            for ps in static_config.KNOWN_FORMS:
                print(ps, ps[:len(pronouns)], pronouns)

            matching = [ps for ps in static_config.KNOWN_FORMS if ps[:len(pronouns)]==pronouns]
            if len(matching) > 2:
                await message.channel.send(f"Hi {name}, more than one pronoun matches. Select one.\n" + "\n".join(
                    "/".join(ps) for ps in matching
                ))
                return
            elif len(matching) == 0:
                await message.channel.send(f"Hi {name}. I don't know all your pronouns. Try again with all five ones. Send `i-am! ?` for more info.`")
                return
            else:
                pronouns = matching[0]

        values = {
            "name": f"**{name}**"
        }

        data = zip(("subject", "object", "possessive_determiner", "possessive", "reflexive"), pronouns)
        for t, v in data:
            values[t] = f"**{v.lower()}**"
            values[f"{t}_t"] = f"**{v.title()}**"

        sentences = (
            static_config.SUBJECT_SENTENCES,
            static_config.OBJECT_SENTENCES,
            static_config.POSSESSIVE_DETERMINER_SENTENCES,
            static_config.POSSESSIVE_SENTENCES,
            static_config.REFLEXIVE_SENTENCES
        )
        lines = [
            f"Hi, {name}! Have fun with these sentences:"
        ]
        for choices in sentences:
            to_print = random.choice(choices)
            lines.append("> " + to_print.format(**values))
        await message.channel.send("\n".join(lines))
            

def main():
    while True:
        try:
            Bot().run()
        except aiohttp.ClientConnectorError:
            continue
        except (KeyboardInterrupt, InterruptedError):
            logging.info("Interrupted")
            return
        except Exception as e:
            logging.error("Something bad happened...", e)
            continue

        return

main()
