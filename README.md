# DoseMate-BHacks24
For Boston Hacks 2024, Reimagine Reality track and Patient Safety Technology Challenge. By Felix Bagurskas Rubio, Mohnish Shridhar, Rohan Chablani and Jay Patel. 

## What is DoseMate?

DoseMate is a proof of concept web app designed to keep medicine users accountable of their use. Users report the time they took the medicine along with their dose. If the user does not report their medicine usage, family members (a given emergency contact) will receive a text message about their missing dose, and can therefore encourage them to follow their prescribed medication schedule. If misuse does occur, the user will also get a notification to explain why they misused their medication. This response will be sent to the patient's medical authority, where they can choose to intervene by suggesting to make an appointment. DoseMate is envisioned as a feature within the patient's Patient Connect / Online Health Provider's app. 

The objective of DoseMate is to **increase patient safety** by keeping patients accountable for their medicine usage. 44% of diagnostic errors are related to medicine use, including but not limited to wrong drug, patient, dose, route and time. In fact, 39% of adverse effects are medication-related, and out of these, 27% are preventable or probably preventable. By keeping patients accountable for their medicine use through their family members or emergency contacts, the rate of adverse effects related to medicine use could diminish. (Statistics from Patient Safety Technology presentation)

## Installation Guide
Make sure the project dependencies are installed: `pip install flask`, `pip install twilio`. You may need to make a [Python virutal environment](https://docs.python.org/3/library/venv.html)--follow the linked tutorial.

Once set up, run `python app.py`.
