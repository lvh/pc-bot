#!/usr/bin/env python
"""Run the bot, as well as the web server."""

import sys
import argparse
import os
import pycon_bot.driver
import pycon_bot.mongo
from pycon_bot.web.app import app as webapp
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from twisted.python import log
from twisted.internet import reactor

def run_bot(irc_server, irc_port, irc_channel, bot_name, http_port, logfile):
    log.startLogging(logfile)
    if irc_server is not None:
        bot = pycon_bot.driver.PyConBotFactory([irc_channel], bot_name)
        reactor.connectTCP(irc_server, irc_port, bot)
    if http_port is not None:
        web = WSGIResource(reactor, reactor.getThreadPool(), webapp)
        reactor.listenTCP(http_port, Site(web))
    reactor.run()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--irc-server', default='irc.freenode.net')
    p.add_argument('--irc-port', type=int, default=6667)
    p.add_argument('--irc-channel', default=os.environ.get('PYCONBOT_CHANNEL', '#pycon-pc'))
    p.add_argument('--irc-nickname', default=os.environ.get('PYCONBOT_NICK', 'pycon_bot'))
    p.add_argument('--http-port', type=int, default=8000)
    p.add_argument('--no-irc', dest='run_irc', action='store_false', default=True)
    p.add_argument('--no-web', dest='run_web', action='store_false', default=True)
    p.add_argument('--dsn', default=None)
    args = p.parse_args()

    # attempt to connect to the mongo db using either
    # the argument passed or the built-in environment variable
    if not pycon_bot.mongo.connect(args.dsn):
        sys.stderr.write("Need to pass --dsn or set env[MONGO_DSN].")
        sys.exit(1)

    # Run ze bot!
    run_bot(
        irc_server=args.irc_server if args.run_irc else None,
        irc_port=args.irc_port,
        irc_channel=args.irc_channel,
        bot_name=args.irc_nickname,
        http_port=args.http_port if args.run_web else None,
        logfile=sys.stderr,
    )
