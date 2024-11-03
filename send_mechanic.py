from twilio.rest import Client



# this is the user account id
account_sid = 'ACef43fdffffcb2378f72d4e0b0fb37878'


# this is the authentication token of the user account
auth_token = '4b4c3d81688e3b560bebd26e1030cb64'
client = Client(account_sid, auth_token)

# this is the phone from which the web application will send the notification from
from_whatsapp_number = 'whatsapp:+14155238886'


# the receiving side phone number
to_whatsapp_number = 'whatsapp:+15088166235'

client.messages.create(body=f"This is a notification to inform you that your loved one ___ has not been following their prescription routine given by their primary care provider. Please get in touch with them. Alert: Multiple doses of MEDICATION NAME logged on DOSAGE DATE. Total: COUNT.",
                    from_=from_whatsapp_number,
                    to=to_whatsapp_number)