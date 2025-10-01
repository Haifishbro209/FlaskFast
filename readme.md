# Get started
```bash
git clone https://github.com/Haifishbro209/FlaskFast.git
```

## 1) set up Virtual environment
```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## 2) set up Oauth2

Open the [GCP](https://console.cloud.google.com/projectselector2)

### Create a new Project
Name it
Select it

### Create Consent Screen
```navigation menu /APIs and Services /Oauth Consent screen```
and click on get started

-external audience

+ ##### Link ToS and Privacy agreement as well as autorized domains in branding

### Create Client

Click on Clients
+ create new client
+ web application
 
+ Authorised redirect URIs ``` http://localhost:8080/oauth2callback ```
Create

+ ##### Download the ```client_secrets_*.json``` file
+ put it somwhere in the repositories folder (don't worry it's in the gitignore)

## 2.2 start the ```.dev/init_project.py``` script

## 3) set up DB


# deploy:
Change the last line of ```app.py``` to disamle debug mode
```python
    app.run(host="0.0.0.0", port=port, debug=False)
```


## example .env file (Not real tokens)
GOOGLE_CLIENT_ID=710982345668-ojhvlsj8l9jn3djnehs2n4b098kn24bgnucbj.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
DB_URL=postgresql://postgres.jnweernftitdblil:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
