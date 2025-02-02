from flask import Flask, render_template, jsonify, request
from make_call import make_call  # Import the make_call function from make_call.py
import random
app = Flask(__name__)
from twilio.rest import Client
# Mock vitals data
def get_mock_vitals():
    return {
        'heart_rate': random.randint(80, 90),
        'blood_pressure': f"{random.randint(120, 140)}/{random.randint(70, 90)}",
        'temperature': round(random.uniform(25, 26), 1),
        'oxygen_level': random.randint(95, 100)
    }

# Sample reminders data
reminders = [
    {
        'id': 1,
        'title': 'Take Medicine',
        'time': '10:00 AM',
        'description': 'Take blood pressure medication'
    },
    {
        'id': 2,
        'title': 'Doctor Appointment',
        'time': '2:30 PM',
        'description': 'Regular checkup with Dr. Smith'
    }
]

# Route to the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to display vitals
@app.route('/vitals')
def vitals():
    return render_template('vitals.html', vitals=get_mock_vitals())

# API to get vitals as JSON
@app.route('/get_vitals')
def get_vitals():
    return jsonify(get_mock_vitals())

# SOS route that triggers an emergency call
@app.route('/sos', methods=['GET', 'POST'])
def sos():
    if request.method == 'POST':
        try:
            make_call()  # Call the function to simulate the emergency call
            return jsonify({"message": "Emergency signal sent! Help is on the way."}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to send emergency signal: {str(e)}"}), 500
    # If the request is GET, render the page
    return render_template('sos.html')

# Route to display reminders
@app.route('/reminders')
def show_reminders():
    return render_template('reminders.html', reminders=reminders)

# Route to face recognition page
@app.route('/face_recognition')
def face_recognition_page():
    return render_template('face.html')

# Route to start face recognition
@app.route('/start_face_recognition')
def start_face_recognition():
    try:
        from face import recognize_faces
        result = recognize_faces()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Route to chatbot page
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')
@app.route('/call')
def make_call():
    # Directly assign your credentials (only for testing)
    # account_sid = "ACe0d9b5f78043ecba291516de2d5c38d8"
    # auth_token = "745ed55b4c1cb004d683e04505782f7b"
    account_sid = 'AC3e580d79e41cd61bb2e20860143d1df3';
    auth_token = 'a9f91fa35a5e5c3504e896438c52f575';

    client = Client(account_sid, auth_token)

    call = client.calls.create(
        url="http://demo.twilio.com/docs/voice.xml",
        # to="+917757910340",  # Your emergency contact number
        # from_="+19403605094",  # Your Twilio number
        to='+918217842832',
        from_='+18314808083',

    )

    print(call.sid)  # This will print the SID of the call, indicating it was placed.
# API to get chatbot responses
@app.route('/chatbot_response', methods=['POST'])
def chatbot_response():
    user_message = request.json.get('message', '').lower()

    if 'emergency' in user_message or 'help' in user_message:
        response = "If you need immediate assistance, please use the SOS button or call emergency services."
    elif 'medicine' in user_message or 'medication' in user_message:
        response = "I can help you set medication reminders. Would you like me to set one up for you?"
    elif 'doctor' in user_message or 'appointment' in user_message:
        response = "I can help you schedule a doctor's appointment. When would you like to schedule it?"
    elif 'vitals' in user_message:
        response = "You can check your vitals in the Vitals section. Would you like me to show you how?"
    else:
        response = "I'm here to help with your healthcare needs. Feel free to ask about emergencies, medications, appointments, or vitals."

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)  # Runs on all available network interfaces