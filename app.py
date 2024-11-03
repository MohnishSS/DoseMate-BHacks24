import json
import send_mechanic
from twilio.rest import Client
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = "data.json"

client = Client(send_mechanic.account_sid, send_mechanic.auth_token)

# Load data from JSON file
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {"users": []}

# Save data to JSON file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Home route: Display users and their medications
@app.route("/")
def home():
    data = load_data()
    data1 = data["users"][0]["medications"].copy()
    for medication in range(len(data1)):
        # Assuming each medication has a 'name' attribute
        string = ""
        
        # Convert each time in 'dosage_times' to 12-hour format and store in list
        formatted_times = []
        for dosage_time in range(len(data1[medication]["dosage_times"])):
            hour, minute = map(int, data1[medication]["dosage_times"][dosage_time].split(':'))
            period = 'AM' if hour < 12 else 'PM'
            hour = hour % 12 or 12  # Convert hour to 12-hour format
            formatted_times.append(f"{hour}:{minute:02d} {period}")
        
        string += f" Dosage times: {', '.join(formatted_times)}\n"
        
        data["users"][0]["medications"][medication]["dosage_times"] = string
    return render_template("home.html", users=data["users"])

# Route to log a dose for a specific medication
from datetime import datetime

@app.route("/log_dose/<int:user_id>", methods=["GET", "POST"])
def log_dose(user_id):
    data = load_data()
    user = next((u for u in data["users"] if u["id"] == user_id), None)

    if not user:
        return "User not found", 404

    if request.method == "POST":
        medication_name = request.form["medication_name"]

        # Check if the 'log_now' button was pressed
        dosage_time = request.form["dosage_time"]
        if dosage_time=="":
            dosage_time = datetime.now().strftime("%H:%M")
        #taken_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dosage_date = date.today().strftime("%m-%d-%Y")

        # Log the dose
        user["log"].append({
            "name": medication_name,
            "dosage_time": dosage_time,
            "dosage_date": dosage_date
        })
        save_data(data)


        # checking for overdoses
        overdoseBool=False
        dose_count=0
        maxDoses=0
        for med in user["medications"]:
            if med["name"]==medication_name:
                maxDoses=len(med["dosage_times"])
                break
        for dose in user["log"]:
            if dose['name']==medication_name:
                dose_count+=1
        if dose_count>maxDoses:
            overdoseBool=True
            return redirect(url_for("explain", user_id=user_id, reason="overdose", med_name = medication_name))
        
        # checking for late dose
        lateBool = False
        dosage_timeInMin = int(dosage_time[:2])*60 + int(dosage_time[3:]) # i am so proud of this formula -Felix :)
        for i in user["medications"]:
            if i["name"] == medication_name:
                mins = []
                for j in i["dosage_times"]:
                    distExpectedAndReal = abs(int(j[:2])*60 + int(j[3:])- dosage_timeInMin)
                    mins.append(distExpectedAndReal)
                if min(mins) > 59:
                    lateBool = True
                    return redirect(url_for("explain", user_id=user_id, reason="late", med_name=medication_name))
        
        
        if not overdoseBool and not lateBool:
            return redirect(url_for("home"))
    
    return render_template("log_dose.html", user=user, current_time=datetime.now().strftime("%H:%M"))


# Route to view compliance for a user
@app.route("/compliance/<int:user_id>")
def compliance(user_id):
    data = load_data()
    user = next((u for u in data["users"] if u["id"] == user_id), None)
    
    if not user:
        return "User not found", 404

    # this part is mostly placeholder. since DoseMate is 'linked' to the patient connect,
    # doctors could give advice to their patients remotely through this part of the app.
    # the user["communication"] field is static in this demo, but could be easily updated
    # if the integration existed. 

    if user["communication"] is not None:
        date = user["communication"][0]
        msg = user["communication"][1]
    else:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
        msg = "No messages available."

    return render_template("compliance.html", user=user, date=date, msg=msg)  # Only pass the user data

@app.route("/explain/<int:user_id>/<reason>/<med_name>", methods=["GET", "POST"])
def explain(user_id, reason, med_name):
    data = load_data()
    # giving the user the opportunity to explain their non-adherence.
    if reason=="late":
        alert_message=f"You took {med_name} on the wrong time. We are sending an alert to your emergency contact and your doctor."
    elif reason=="overdose":
        alert_message=f"You took {med_name} more than you were supposed to today. We are sending an alert to your emergency contact and your doctor."
    
    # sending the message to the family member.
    if request.method == "POST":
        reason_message = request.form["message"]
        if reason=="overdose":
            client.messages.create(body=f"This is a notification to inform you that your loved one has not been following their prescription routine given by their primary care provider. Please get in touch with them. Alert: Possible overdose of {med_name}. Here is what he said: {reason_message}",
                        from_=send_mechanic.from_whatsapp_number,
                        to=send_mechanic.to_whatsapp_number)
        elif reason=="late":
            client.messages.create(body=f"This is a notification to inform you that your loved one has not been following their prescription routine given by their primary care provider. Please get in touch with them. Alert: Missed the schedule for {med_name}. Here is what he said: {reason_message}",
                        from_=send_mechanic.from_whatsapp_number,
                        to=send_mechanic.to_whatsapp_number)

    # a similar message could be sent to doctors/medical professionals.
    # we work under the assumption that DoseMate is linked to Patient Connect
    # and therefore these communication channels already exist and are easily
    # callable and editable.

        return redirect(url_for("home"))
    return render_template("explain.html", users=data["users"], alert=alert_message)

if __name__ == "__main__":
    app.run(debug=True)
