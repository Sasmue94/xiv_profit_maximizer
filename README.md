# xiv_profit_maximizer
xiv profit maximizer to minimize crafting cost and maximize profits
uses data from xivapi (xivapi.com) and universalis (universalis.app)
consider supporting those, without them, this project wouldn't be possible.

installation instructions:

- clone repository

- open your terminal
- navigate to the project directory
    -> cd /path/to/your/project

- create a virtual enviroment
    -> python -m venv myenv

- activate your virtual enviroment
Windows:
    -> myenv\Scripts\activate

Linux / macOS:
    -> source myenv/bin/activate

- once your enviroment is activated install requirements
    -> pip install -r requirements.txt

run app:

- make sure your enviroment is activated 
- in your terminal:
    -> streamlit run app.py
    -> The webui should run in your browser

close app:

- while your app is running navigate to your open terminal (the one you started the app with)
    -> ctrl + c
    -> the process should shut down
    (you can also end your python process via windows taskmanager or kill <pid> on Linux)

- close browser window

once done:

- deactivate your python enviroment, in your terminal:
    -> deactivate