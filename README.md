# Telegram 

### Endpoints
- User already has a Telegram account and wants to log into this app
> If the user has not joined previously, they will be sent a code to an active Telegram session or SMS
> This code should be requested for and sent to the backend to finish the joining  process

```json
POST /join
body:
{
	"phonenumber":"[country_code][number]"
}
```

response:
```html
100 - awaiting code from user
400 - user is not registered (they can be registered, see endpoing below)
200 - user already present
```

- User has not joined Telegram before
```json
POST /register
body:
{
	"phonenumber":"[country_code][number]",
	"first_name":"",
	"last_name":""
}
```

response:
```html
400 - failed to create user
200 - user created successfully
```
