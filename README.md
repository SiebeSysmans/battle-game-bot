# Battle Game Bot

This is a bot for automatically managing units and resources in a text based mobile game and was deployed during the public testing phase.

The name of the game has been omitted to not allow further disruption post-launch.

## Features

- Automatically buy items
- Automatically create and train units
- Automatically convert units to another type
- Post job results to a Telegram chat

## Requirements

Several environment variables are necessary to fully run the bot. These can either be supplied by setting them on the machine that runs the bot or by putting them in a file under `src/.env`.

```properties
API_ENDPOINT = <Endpoint of the api>
DATABASE_URL = <URL for the database with username and password>
TELEGRAM_TOKEN = <Token for the Telegram bot>
TELEGRAM_CHAT_ID = <Chat ID between the bot and monitoring user>
INITIAL_TOKEN = <Bearer token to initialize the API>
```
## Usage

### Local

To run this on a local machine, first use pip to install dependencies.

```bash
pip3 install -r requirements.txt
```

Then run the app with python.

```bash
python3 src/runner.py
```

### Heroku

This project is ready to run on [Heroku](https://heroku.com) because of the included `Procfile`.

Just push this project to an empty Heroku app and you're good to go!

## License

```
MIT License

Copyright (c) 2021 Siebe Sysmans

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
