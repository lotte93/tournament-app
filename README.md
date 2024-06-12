# Tournament app

This repository contains code for a Streamlit app to be used for amateur tournaments. Given a tournament schedule in 
a Google Docs Spreadsheet, it shows the upcoming matches, let's you fill in match results, shows the tournament standings and determines the knockout matches.

## Get started

### Local development
1. Create a spreadsheet with the tournament schedule. 
2. Add password to open app to .streamlit/secrets.toml.
3. Store the secrets to connect with the spreadsheet in .streamlit/secrets.toml.
4. Create local environment with requirements from requirements.txt
5. Run app: streamlit run app.py

### Deploy on Streamlit Cloud
1. Create a spreadsheet with the tournament schedule.
2. Create account on Streamlit Cloud and deploy app
3. When deploying click "Advanced settings" and add secrets as shown below
4. Share the app with others

### Example secrets.toml:

```
password = ""

[connections.gsheets]
spreadsheet = ""

type = "service_account"
project_id = ""
private_key_id = ""
private_key = ""
client_email = ""
client_id = ""
auth_uri = ""
token_uri = ""
auth_provider_x509_cert_url = ""
client_x509_cert_url = ""
```