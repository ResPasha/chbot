# Feedback bot
Telegram bot which helps me with handling feedback from channel subscribers

## Setup
You need a `config.py` with those variables defined:
```python
master = '<your_userid>'
TOKEN = '<telegram_bot_token>'
db_auth = 'mongodb://<user>:<password>@<my.mongodb.com>:<port>/<database>'  # your MongoDB connection url
db_name = '<database_name>'
```
You can get <user_id> from @userinfobot

## Starting bot
```
./app.py
```

## Usage
Bot forwards all messages to Master.
To reply from Bot to user, simply reply to forwarded message and Bot will resend your reply.