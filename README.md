# Maid-chan bot
Telegram bot which helps me with channel uploads

## Setup
You need a `config.py` with those variables defined:
```python
channel = '<@main_channel_username | userid>'
nsfw_channel = '<@nsfw_channel_username | userid>'
master = '<master_userid>'
TOKEN = '<telegram_bot_token>'
db_auth = 'mongodb://<mongo_db_URI>'
db_name = '<database_name>'
```
You can use userid instead of any `@channel_name` for publishing to specified user instead of channel.
It is useful for testing.

MongoDB should already have tho collections. Their names aer specified in `db_helper.cr_coll_name` and `db_helper.img_coll_name`.

## Usage
```
./chbot.py &
```
