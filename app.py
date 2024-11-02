import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = "data.json"

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
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
            print("Data saved successfully.")  # Debugging statement
    except Exception as e:
        print("Failed to save data:", e)  # Debugging statement

# Home route: Display users and their medications
@app.route("/")
def home():
    data = load_data()
    return render_template("home.html", users=data["users"])

# Route to log a dose for a specific medication
@app.route("/log_dose/<int:user_id>", methods=["GET", "POST"])
def log_dose(user_id):
    data = load_data()
    user = next((u for u in data["users"] if u["id"] == user_id), None)

    if not user:
        return "User not found", 404

    if request.method == "POST":
        medication_name = request.form["medication_name"]
        dosage_time = request.form["dosage_time"]
        taken_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log the dose if it matches one of the scheduled times
        valid_medication = any(
            med["name"] == medication_name and dosage_time in med["dosage_times"]
            for med in user["medications"]
        )
    
        if valid_medication:
            user["log"].append({
                "name": medication_name,
                "dosage_time": dosage_time,
                "taken_at": taken_at
            })
            save_data(data)
            return redirect(url_for("home"))
        else:
            return "Invalid medication or dosage time", 400
    
    return render_template("log_dose.html", user=user)

# Route to view compliance for a user
@app.route("/compliance/<int:user_id>")
def compliance(user_id):
    data = load_data()
    user = next((u for u in data["users"] if u["id"] == user_id), None)
    
    if not user:
        return "User not found", 404

    compliance_data = calculate_compliance(user)
    return render_template("compliance.html", user=user, compliance=compliance_data)

# Calculate compliance rate
def calculate_compliance(user):
    scheduled_doses = sum(len(med["dosage_times"]) for med in user["medications"])
    compliant_doses = len(user["log"])
    compliance_rate = (compliant_doses / scheduled_doses * 100) if scheduled_doses > 0 else 0
    return {"rate": compliance_rate, "total": scheduled_doses, "compliant": compliant_doses}



@app.route("/communication/<int:user_id>")
def communication(user_id):
    data = load_data()
    user = next((u for u in data["users"] if u["id"] == user_id), None)
    
    if not user:
        return "User not found", 404
    
    communication_data = return_communication(user)
    return render_template("communication.html", user=user, communication_data=communication_data)

def return_communication(user):
    return "sample message for now. edit with real message from json later."

if __name__ == "__main__":
    app.run(debug=True)
