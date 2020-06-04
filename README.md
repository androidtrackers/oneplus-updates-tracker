# OnePlus Updates Tracker

[![Subscibe](https://img.shields.io/badge/Telegram-Subscribe-blue.svg)](https://t.me/OnePlusUpdatesTracker)

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue.svg)](https://www.paypal.me/yshalsager)

A Python 3 script that automatically tracks OnePlus Oxygen OS and Hydrogen OS ROMs releases and send messages of new updates to telegram channel to notify users!

It currently uses OnePlus official websites as the only updates source, and supports all devices.

#### Running it on your own:

- You need Python 3.6 at least and pip 19 installed on your device.
- Install the requirements using `pip install .`
- Copy `config.yml.example` to `config.yml` and fill it with the following:
  
  ```yml
  tg_bot_token:  # Telegram bot token, get it from @BotFather
  tg_chat:  # Telegram chat username or ID
  git_oauth_token:  # GitHub OAuth token
  source: "official"
  ```
