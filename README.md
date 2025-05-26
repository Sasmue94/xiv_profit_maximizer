# xiv_profit_maximizer
xiv profit maximizer to minimize crafting cost and maximize profits when crafting.
shows material sources and cheapest possible combination of buyouts and visualizes
shopping data.

uses data from xivapi (xivapi.com) and universalis (universalis.app)
consider supporting those, without them, this project wouldn't be possible.

# installation:

- clone repository

- open your terminal
- navigate to the project directory

```
cd /path/to/your/project
```

## _create a virtual enviroment (optional)_

```
_python -m venv myenv_
```

- _activate your virtual enviroment (optional)_
_Windows:_

```
myenv\Scripts\activate
```

_Linux / macOS:_

```
source myenv/bin/activate
```

## install requirements
```
pip install -r requirements.txt
```

# run app:

- _make sure your enviroment is activated (optional)_

in your terminal:

```
streamlit run app.py
```    

The webui should run in your browser

## close app:

- while your app is running navigate to your open terminal (the one you started the app with)
    - ctrl + c
    - the process should shut down
    _(you can also end your python process via windows taskmanager or kill <pid> on Linux)_

- close browser window