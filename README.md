# Telegram 

### Endpoints
- User already has a Telegram account and wants to log into this app
> If the user has not joined previously, they will be sent a code to an active Telegram session or SMS
> This code should be requested for and sent to the backend to finish the joining  process

Join SWoB Telegram App: `POST /join`
```json
{
	"phonenumber":"[country_code][number]"
}
```

_response status code_
Awaiting code from user - `100`
User is not registered (they can be registered, see endpoing below) - `101`
User already present - `200`

Register for new Telegram account `POST /register`
```json
{
	"phonenumber":"[country_code][number]",
	"first_name":"",
	"last_name":""
}
```

_response status code_
Failed to create user - `400`
User created successfully - `200`
```
