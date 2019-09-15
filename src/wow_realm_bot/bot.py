import sys
import argparse
import logging
import re

import attr
import discord

from .wow import CachedRealmStatusProvider

MINUTE = 60

class WowBot(discord.Client):

    def __init__(self, status_provider):
        super().__init__()
        self.status_provider = status_provider
        self.log = logging.getLogger(self.__class__.__name__)

    async def on_message(self, message):
        # Ignore messages we write
        if message.author == self.user:
            return
        # Process message
        msg = message.content.lower()
        m = re.match("!realm", msg)
        if m:
            self.log.info(f"Processing command '{message}'")
            status_map = self.status_provider.getAllRealmStatuses()
            status = status_map.getStatusByName("stalagg")
            self.log.info(f"Got result {status}")
            await message.channel.send(f"`{status.name} -> {status.population}`")

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, required=True, help="Your discord bot token.")
    parser.add_argument("--debug", action='store_true')
    return parser.parse_args(argv[1:])

def main(argv):
    # Parse arguments
    args = parse_args(argv)
    # Get the token they set
    token = args.token
    # Setup logging
    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level)
    # Make the client
    provider = CachedRealmStatusProvider(15 * MINUTE)
    client = WowBot(provider)
    # Enter event loop
    client.run(token)

def cli():
    main(sys.argv)

if __name__ == '__main__':
    cli()