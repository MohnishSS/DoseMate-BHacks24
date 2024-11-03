from twilio.rest import Client


# this is the user account id
account_sid = 'ACef43fdffffcb2378f72d4e0b0fb37878'


# this is the authentication token of the user account
auth_token = '8d459c04119e1f1163ed19b1544e86f1'


# creates a client object
client = Client(account_sid, auth_token)


# this is the phone from which the web application will send the notification from
from_whatsapp_number = 'whatsapp:+14155238886'


# the recieving side phone number
to_whatsapp_number = 'whatsapp:+15088166235'


# this call will send a message
# client.messages.create(body='This is a notification to inform you that you loved on <name of patient> has not been following their prescription routine given by their primary care provider. Please get in touch with <name of patient>.',
#                      from_=from_whatsapp_number,
#                      to=to_whatsapp_number)
