import os
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from pyngrok import ngrok

load_dotenv()

# Slack Credentials
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Salesforce Credentials
SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
SF_USERNAME = os.getenv("SF_USERNAME")
SF_PASSWORD = os.getenv("SF_PASSWORD")

# Initialize Flask & Slack App
flask_app = Flask(__name__)
slack_app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
handler = SlackRequestHandler(slack_app)


# Function to authenticate with Salesforce
def create_salesforce_lead(first_name, last_name, email, company, phone):
    # Salesforce API endpoint for creating a Lead
    access_token = os.getenv("access_token")
    instance_url = os.getenv("instance_url")

    url = f"{instance_url}/services/data/v58.0/sobjects/Lead/"

    # Headers for the request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Lead data to create
    lead_data = {
        "FirstName": first_name,
        "LastName": last_name,
        "Company": company,
        "Email": email,
        "Phone": phone,
        "Status": "Open - Not Contacted"
    }

    # POST request to create the Lead
    try:
        response = requests.post(url, json=lead_data, headers=headers)
        response.raise_for_status()

        lead_id = response.json()["id"]
        print("Lead created successfully!")
        print("Lead ID:", lead_id)

        return lead_id

    except requests.exceptions.HTTPError as err:
        print("HTTP Error:", err)
        return None
    except Exception as err:
        print("Error:", err)
        return None


# Flask Route to Handle Slack command
@flask_app.route("/slack/slashcommand", methods=["POST"])
def slack_slash_command():
    fname, lname, email = request.form.get("text").split(' ')
    create_salesforce_lead(first_name=fname, last_name=lname, email=email, company='3x and co', phone='1234567890')

    response_url = request.form.get("response_url")
    response_payload = {
        "response_type": "in_channel",
        "text": f" Lead created successfully"
    }

    # Send response back to Slack using the response_url
    requests.post(response_url, json=response_payload)

    return ''


if __name__ == "__main__":
    # Start ngrok tunnel
    # public_url = ngrok.connect(5000).public_url
    # print(f"🚀 Ngrok Tunnel: {public_url}/slack/slashcommand")

    # Run Flask app
    flask_app.run(port=5000, debug=True)


