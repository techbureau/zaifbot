"""execute zaifbot

usage: zaifbot [--config-path=[config-path]]

options:
    [--config-path=[config-path]]            config path [./conf.json]
"""
from zaifbot.modules.auto_trade.daemon import start_auto_trade_daemon


def main():
    start_auto_trade_daemon()
