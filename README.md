# How to use this script

## Install requirements

```console
pip3 install -r requirements.txt
```

## Enable all mediun severity policies

In the main() function, uncomment following lines to edit policies:  

```python
changePolicyStatusPerSeverity(API_ENDPOINT, token, 'medium', 'true')
```
## Disable all low severity policies

In the main() function, uncomment following lines to edit policies:  

```python
changePolicyStatusPerSeverity(API_ENDPOINT, token, 'low', 'false')
```

## Run the script

```console
python3 main.py
```

