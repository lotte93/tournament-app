# Tournament app

This repository contains code for a Streamlit app to be used for amateur tournaments. Given a tournament schedule in 
a Google Docs Spreadsheet, it shows the upcoming matches, let's you fill in match results, shows the tournament standings and determines the knockout matches.

## Get started
1. Create a spreadsheet with the tournament schedule. 
2. Store the secrets to connect with the spreadsheet in .streamlit/secrets.toml.
3. Add admin user emailadresses to secrets.toml. These people will be authorized to write results.

### Example secrets.toml:

```[connections.gsheets]
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

[authorization]
emails = ["", ""]
```