import json
import send_mechanic
from twilio.rest import Client
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = "data.json"

#client = Client(send_mechanic.account_sid, send_mechanic.auth_token)

# Load data from JSON file
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            print("Data loaded:", data)  # Debugging statement
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

        # Judges: We are so proud of this code! 
        # it determines whether a taken dose is late
        lateBool = False
        dosage_timeInMin = int(dosage_time[:2])*60 + int(dosage_time[3:])
        for i in user["medications"]:
            if i["name"] == medication_name:
                for j in i["dosage_times"]:
                    mins = []
                    distExpectedAndReal = abs(int(j[:2])*60 + int(j[3:])- dosage_timeInMin)
                    mins.append(distExpectedAndReal)
                if min(mins) > 59:
                    lateBool = True
        
        print(lateBool)

        # Log the dose
        user["log"].append({
            "name": medication_name,
            "dosage_time": dosage_time,
            "dosage_date": dosage_date
        })
        save_data(data)
        
        if lateBool:
            return redirect(url_for("explain", user_id=user_id, reason="late", med_name = medication_name))
        else:
            return redirect(url_for("home"))
    
    return render_template("log_dose.html", user=user, current_time=datetime.now().strftime("%H:%M"))


# Route to view compliance for a user
@app.route("/compliance/<int:user_id>")
def compliance(user_id):
    data = load_data()
    user = next((u for u in data["users"] if u["id"] == user_id), None)
    
    if not user:
        return "User not found", 404
    
    alerts = []
    medication_count = {}
    
    for dose in user["log"]:
        #print(f"{dose['name']}_{dose['dosage_date']}")
        date_key = f"{dose['name']}_{dose['dosage_date']}"
        if date_key in medication_count:
            medication_count[date_key] += 1
        else:
            medication_count[date_key] = 1
            
    for med_date, count in medication_count.items():
        if count > 1:
            medication_name, dosage_date = med_date.split('_')
            alerts.append(f"Alert: Multiple doses of {medication_name} logged on {dosage_date}. Total: {count}.")
            # client.messages.create(body=f"This is a notification to inform you that your loved one ___ has not been following their prescription routine given by their primary care provider. Please get in touch with them. Alert: Multiple doses of {medication_name} logged on {dosage_date}. Total: {count}.",
            #         from_=send_mechanic.from_whatsapp_number,
            #         to=send_mechanic.to_whatsapp_number)
            
    

    
    if user["communication"] is not None:
        date = user["communication"][0]
        msg = user["communication"][1]
    else:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
        msg = "No messages available."

    return render_template("compliance.html", user=user, alerts=alerts, date=date, msg=msg)  # Only pass the user data

@app.route("/explain/<int:user_id>/<reason>/<med_name>")
def explain(user_id, reason, med_name):
    data = load_data()
    if reason=="late":
        alert_message=f"You took {med_name} on the wrong time. We are sending an alert to your emergency contact and your doctor."
    return render_template("explain.html", users=data["users"], alert=alert_message)

if __name__ == "__main__":
    app.run(debug=True)
