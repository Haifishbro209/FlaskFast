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

Create a new Project

## How to deploy:
Change the last line of ```app.py``` to disamle debug mode
```python
    app.run(host="0.0.0.0", port=port, debug=False)
```