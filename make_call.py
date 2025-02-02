# make_call.py
from twilio.rest import Client

def make_call():
    # Directly assign your credentials (only for testing)
    account_sid = "ACe0d9b5f78043ecba291516de2d5c38d8"
    auth_token = "745ed55b4c1cb004d683e04505782f7b"
    
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        url="http://demo.twilio.com/docs/voice.xml",
        to="+917757910340",  # Your emergency contact number
        from_="+19403605094",  # Your Twilio number
    )

    print(call.sid)  # This will print the SID of the call, indicating it was placed.