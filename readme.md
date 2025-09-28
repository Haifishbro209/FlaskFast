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

##### Link ToS and Privacy agreement as well as autorized domains in branding


# deploy:
Change the last line of ```app.py``` to disamle debug mode
```python
    app.run(host="0.0.0.0", port=port, debug=False)
```