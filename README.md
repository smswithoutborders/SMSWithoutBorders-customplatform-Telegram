# Telegram 

### HTTP API Endpoints

<a name="start_session"></a>
###### Start a session 
> `POST /`
```json
{
	"phonenumber":"[country_code][number]"
}
```
> * If the user already has an active session, a `200` is sent back
> * If the user does not have an active session a `201` is sent back and a code is sent either to their Telegram App or via SMS. 
> You should request and provide this code to finish the start session process. See [Provide Code](#provide_code)

<a name="provide_code"></a>
###### Provide the sent session code
> `PUT /`
```json
{
	"phonenumber":"[country_code][number]",
	"code":"[code]"
}
```
> * If the user does not have a Telegram account a `202` is sent back. See [Register user](#register_user)
> * If the code is wrong a `403` is sent back.
> * If the code is correct a `200` is sent back and an `md5` hash of the phone number

<a name="register_user"></a>
###### Register user
- To continue using SWoB App, user must register a Telegram account by providing first and last name
> `POST /users`
```json
{
	"phonenumber":"[country_code][number]",
	"first_name":"",
	"last_name":""
}
```
> * Returns `200` if successful and `500` for any error

<a name="delete_user"></a>
###### Delete user
- Deleting the record of a user stored on local server. (Does not delete user from Telegram global server)
> `DELETE /users`
```json
{
	"phonenumber_hashed":"[MD5 Hashed phone number]",
}
```
> * Returns `200` if successful and `500` for any error
