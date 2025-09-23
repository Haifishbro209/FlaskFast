# Get started

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

## 2) set up Oauth

## How to deploy:
Change the last line of ```app.py``` to disamle debug mode
```python
    app.run(host="0.0.0.0", port=port, debug=False)
```