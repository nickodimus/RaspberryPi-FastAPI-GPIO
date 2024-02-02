# https://dev.to/climentea/can-you-use-fastapi-vue-react-other-to-create-a-desktop-application-34gd


from flaskwebgui import FlaskUI
from main import app

FlaskUI(app, start_server='fastapi', width=600, height=500).run()
# run with
# python gui.py