# Telegram

## Requirements

- [Python](https://www.python.org/) (version >= [3.8.10](https://www.python.org/downloads/release/python-3810/))
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Obtain your telegram credentials](https://core.telegram.org/api/obtaining_api_id)

## Installation

Create a Virtual Environments **(venv)**

```
python3 -m venv venv
```

Move into Virtual Environments workspace

```
. venv/bin/activate
```

Install all python packages

```
python -m pip install -r requirements.txt
```

## Configurations

Copy `example.configs.ini` to `configs.ini`

```bash
cp configs/example.configs/ini configs/configs.ini
```

## How to use

### Start telegram api

```bash
python3 telegram_api.py
```

set log levels with the `logs` variable. Default = "INFO"

```bash
logs=debug python3 telegram_api.py
```

## API Endpoints

### Start a session

> `POST /`

```json
{
  "phonenumber": "[country_code][number]"
}
```

> - If the user already has an active session, a `200` is sent back
> - If the user does not have an active session a `201` is sent back and a code is sent either to their Telegram App or via SMS.
>   You should request and provide this code to finish the start session process. See [Provide Code](#Provide-the-sent-session-code)

### Provide the sent session code

> `PUT /`

```json
{
  "phonenumber": "[country_code][number]",
  "code": "[code]"
}
```

> - If the user does not have a Telegram account a `202` is sent back. See [Register user](#register-user)
> - If the code is wrong a `403` is sent back.
> - If the code is correct a `200` is sent back and an object

```json
{
  "phonenumber": "",
  "profile": {}
}
```

### Register user

- To continue using SWoB App, user must register a Telegram account by providing first and last name
  > `POST /users`

```json
{
  "phonenumber": "[country_code][number]",
  "first_name": "",
  "last_name": ""
}
```

> - Returns `200` if successful and `500` for any error

### Delete user

- Deleting the record of a user stored on local server. (Does not delete user from Telegram global server).
  > `DELETE /users`

```json
{
  "phonenumber": "[country_code][number]"
}
```

> - Returns `200` if successful and `500` for any error

### Get all telegram contacts

- Fetch all user's telegram contacts
  > `POST /contacts`

```json
{
  "phonenumber": "[country_code][number]"
}
```

> - Returns `200` if successful and `500` for any error

### Get all active dialogs

- Fetch all user's active telegram chats
  > `POST /dialogs`

```json
{
  "phonenumber": "[country_code][number]"
}
```

> - Returns `200` if successful and `500` for any error

### Send message

- Send a telegram message
- If the recipient's contact is not in the user's contact list, it will be imported automatically in order for the telegram message to be sent.
  > `POST /message`

```json
{
  "phonenumber": "[country_code][number]",
  "recipient": "[country_code][number] or username or user ID",
  "text": "Hello World!"
}
```

> - If the `recipient` does not have a telegram account a `422` is sent back.
> - Returns `200` if successful and `500` for any error
