from typing import Optional, List
import os
import socket
import datetime as dt
from fastapi import Depends, FastAPI, HTTPException, Request, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
import json
import urllib.request

# local imports
from src.db.db import get_session, sqlite_engine_gpio
from src.db.models_gpio import GPIO, GPIOSelect, GPIORead, GPIOUpdate
from templates.components.schemas import GPIOForm, idForm, initializationForm


app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Define Local Variables
hostname = socket.gethostname()
ipAddress = "10.10.0.32"

welcomeGPIO = "GPIO Control Interface"
welcomeHome = "GPIO Home Page"
welcomenodeRed = "Node-RED Server"
welcomeXTerm = "Embedded Terminal Page"
welcomeInitialize = "GPIO Initialization Page"
welcomeInitializeResponse = "GPIO Persistence Activated"
interactiveGPIOPinout = "https://pinout.xyz/"
table_pic = "/static/images/happy.png"


'''
Set the startup stuff into a login page endpoint so 
when you login it will redirect you to the home page and load al the gpios

---> OR use the htmx code here which is also documented in /templates/gpio.html:

<div hx-get="/" hx-target="#gpios" hx-trigger="load">
    <img  alt="Result loading..." class="htmx-indicator" width="150" src="/img/bars.svg"/>
</div>
'''
# You can combine FastAPI features like automatic path parameter validation to get models by ID.


@app.on_event("startup")
async def set_gpio():
    """
    Asynchronous function to set up GPIO on startup and start wssh on 10.10.0.32.
    """
    shellCommand = str(f"wssh --address""=""{ipAddress}")
    os.system(shellCommand)
    with Session(sqlite_engine_gpio) as session:
        gpios = session.exec(select(GPIO)).all()


@app.get("/home", response_class=HTMLResponse)
def loadHome(request: Request):
    """
    Load the home page and return an HTML response.

    Parameters:
        request (Request): The incoming request object.

    Returns:
        TemplateResponse: The HTML response for the home page.
    """
    context = {"request": request, "name": welcomeHome}
    return templates.TemplateResponse("general_pages/home.html", context)


@app.get("/initialize", response_class=HTMLResponse)
async def get_initialize(request: Request, hx_request: Optional[str] = Header(None)):
    """
    Get the initialize endpoint. Takes a request and an optional hx_request header.
    Returns an HTMLResponse with the appropriate context.
    """
    context = {"request": request, "name": welcomeInitialize}
    hx_context = {"request": request, "name": welcomeInitialize}
    if hx_request:
        return templates.TemplateResponse("general_pages/initialize.html", hx_context)
    return templates.TemplateResponse("general_pages/initialize.html", context)


@app.post("/initialize", response_class=HTMLResponse)
async def post_initialize(request: Request, hx_request: Optional[str] = Header(None), form_data: initializationForm = Depends(initializationForm.as_form)):
    """
    A function to handle POST requests to '/initialize', with parameters request, hx_request, and form_data.
    It sets up GPIO permissions and returns an HTMLResponse to confirm the status of the permissions of
    /dev/gpiomem

    Check that /dev/gpiomem has the correct permissions.

    ls -l /dev/gpiomem

    crw-rw---- 1 root gpio 244, 0 Dec 28 22:51 /dev/gpiomem

    If it doesn't then set the correct permissions as follows

    sudo chown root:gpio /dev/gpiomem
    sudo chmod g+rw /dev/gpiomem
    """
    form_data = dict(form_data)
    # Extracting key-value of dictionary in variables
    password = list(form_data.values())[1]

    shellCommand = (f"echo {password} | sudo -S chown root:gpio /dev/gpiomem && sudo chmod g+rw /dev/gpiomem")
    os.system(shellCommand)
    status = os.system("ls -l /dev/gpiomem")

    statusExpected = "crw-rw---- 1 root gpio 244, 0 /dev/gpiomem"

    context = {"request": request, "name": welcomeInitializeResponse}
    hx_context = {"request": request, "name": welcomeInitializeResponse, "statusExpected": statusExpected, "status": status}
    if hx_request:
        return templates.TemplateResponse("general_pages/initializeConfirmation.html", hx_context)
    return templates.TemplateResponse("general_pages/initializeConfirmation.html", context)


@app.get("/", response_model=List[GPIO], response_class=HTMLResponse)
async def get_gpio(request: Request, hx_request: Optional[str] = Header(None), *, session: Session = Depends(get_session)):
    """
    Get GPIO data and Nasa's Astronomy Picture of the Day for the HTML response.

    Parameters:
    - request: Request
    - hx_request: Optional[str] = Header(None)
    - session: Session = Depends(get_session)

    Returns:
    - TemplateResponse: "components/gpio.html" if hx_request is provided
    - TemplateResponse: "general_pages/gpio.html" if hx_request is not provided
    """
    # Nasa's Astronomy Picture of the Day
    '''
    apod_url = urllib.request.urlopen(
        "https://api.nasa.gov/planetary/apod?api_key=6AFdWx2zcPvtlUT7T9EU4Gtcnfge1QIqDjObalYL")
    apod_url = apod_url.read().decode("utf-8")
    apod_url = json.loads(apod_url)
    #print(apod_url)
    apod_pic = (apod_url['url'])
    #print(table_pic)
    '''
    # return All GPIOs
    gpios = session.exec(select(GPIO)).all()
    #context = {"request": request, "name": welcomeGPIO, "gpios": gpios, "apod_pic": apod_pic}
    #hx_context = {"request": request, "gpios": gpios, "apod_pic": apod_pic}

    # return offline_*_context when running app offline
    offline_hx_context = {"request": request, "gpios": gpios}
    offline_context = {"request": request, "name": welcomeGPIO, "gpios": gpios}
    #print(f"from @app.get / endpoint >> {gpios}")

    if hx_request:
        return templates.TemplateResponse("components/gpio.html", offline_hx_context)
    return templates.TemplateResponse("general_pages/gpio.html", offline_context)


@app.post("/", response_class=HTMLResponse)
async def update_GPIOs(request: Request, hx_request: Optional[str] = Header(None), form_data: GPIOForm = Depends(GPIOForm.as_form)):
    """
    Submit form data to the server and update the database with the selected GPIO data.

    Args:
        request (Request): The incoming request object.
        hx_request (str, optional): The hx_request header value. Defaults to None.
        form_data (GPIOForm): The form data containing GPIO information.

    Returns:
        HTMLResponse: A response containing HTML content.
    """
    #print(form_data)
    form_data = dict(form_data)
    changed_key = "changed"
    changed_val = dt.datetime.now().strftime("%a %b %d %Y %I:%M:%S %p")

    form_data[changed_key] = changed_val

    #print(form_data)

    # Extracting key-value of dictionary in variables
    gpio_key = list(form_data.keys())[0]
    gpio_val = list(form_data.values())[0]
    type_key = list(form_data.keys())[1]
    type_val = list(form_data.values())[1]
    state_key = list(form_data.keys())[2]
    state_val = list(form_data.values())[2]
    usedfor_key = list(form_data.keys())[3]
    usedfor_val = list(form_data.values())[3]
    changed_key = list(form_data.keys())[4]
    changed_val = list(form_data.values())[4]

    # Returning a confirmation message
    #print(gpio_val, usedfor_val, type_val, state_val, changed_val)

    # Update the database with the selected GPIO data
    id = gpio_val
    with Session(sqlite_engine_gpio) as session:
        db_GPIO = session.get(GPIO, id)
        if not db_GPIO:
            raise HTTPException(status_code=404, detail="GPIO not found")
        for key, value in form_data.items():
            setattr(db_GPIO, key, value)
        session.add(db_GPIO)
        session.commit()
        session.refresh(db_GPIO)

    with Session(sqlite_engine_gpio) as session:
        gpios = session.exec(select(GPIO)).all()

    os.system(f" python ./scripts/GPIO_set.py --gpio={gpio_val} --type={type_val} --state={state_val}")

    hx_context = {"request": request, "gpios": gpios}
    context = {'request': request, "name": welcomeGPIO, "gpios": gpios}
    if hx_request:
        return templates.TemplateResponse("components/gpio.html", hx_context)
    return templates.TemplateResponse("general_pages/gpio.html", context)


@app.get("/gpio/", response_model=List[GPIO])
def read_GPIOs(*, session: Session = Depends(get_session)):
    """
    Read all GPIO entries and return a list of GPIO objects.

    Returns:
        List[GPIO]: List of GPIO objects.
    """
    gpios = session.exec(select(GPIO)).all()
    context = {"name": welcomeGPIO, "gpios": gpios}
    return templates.TemplateResponse("general_pages/gpio.html", context)


@app.patch("/gpio/{id}", response_model=GPIORead)
def update_GPIO(id: int, gpio: GPIOUpdate):
    """
    Update GPIO by id with new data and return the updated GPIO object.
    Params:
    - id: int
    - gpio: GPIOUpdate
    Returns:
    - GPIORead
    Raises:
    - HTTPException: If GPIO not found
    """
    with Session(sqlite_engine_gpio) as session:
        db_GPIO = session.get(GPIO, id)
        if not db_GPIO:
            raise HTTPException(status_code=404, detail="GPIO not found")
        gpio_data = gpio.model_dump(exclude_unset=True)
        for key, value in gpio_data.items():
            setattr(db_GPIO, key, value)
        session.add(db_GPIO)
        session.commit()
        session.refresh(db_GPIO)
        gpios = session.exec(select(GPIO)).all()
        return db_GPIO


@app.post("/idForm", response_model=List[GPIO], response_class=HTMLResponse)
def read_GPIO(request: Request, hx_request: Optional[str] = Header(None), form_data: idForm = Depends(idForm.as_form)):
    """
    Read GPIO from idForm and return HTMLResponse
    Args:
        request: Request - The incoming request
        hx_request: Optional[str] - Header value
        form_data: idForm - Form data

    Returns:
        List[GPIO]: List of GPIO objects
    """
    form_data = dict(form_data)
    # Extracting key-value of dictionary in variables
    gpio_key = list(form_data.keys())[0]
    id = list(form_data.values())[0]

    with Session(sqlite_engine_gpio) as session:
        gpios = session.exec(select(GPIO).where(GPIO.gpio == id))
        print(f"from sql response {gpios}")
        context = {"request": request, "name": welcomeGPIO, "gpios": gpios}
        hx_context = {"request": request, "name": welcomeGPIO, "gpios": gpios}
        if hx_request:
            return templates.TemplateResponse("components/gpio.html", hx_context)
        return templates.TemplateResponse("general_pages/gpio.html", context)


@app.get("/nodeRed", response_class=HTMLResponse)
def nodeRed(request: Request):
    """
    This function handles the GET request for '/nodeRed' and returns an HTML response.

    Args:
        request (Request): The request object

    Returns:
        TemplateResponse: The HTML response with the context
    """
    #ipAddress = socket.gethostbyname(socket.gethostname())
    print(ipAddress)
    context = {"request": request, "name": welcomenodeRed, "ipAddress": ipAddress}
    return templates.TemplateResponse("general_pages/nodeRed.html", context)


@app.get("/terminal", response_class=HTMLResponse)
def loadXTerm(request: Request):
    """
    Function to handle GET requests to /terminal and load XTerm, taking a Request object as parameter and returning an HTMLResponse.
    Inspired from: https://github.com/samuelcolvin/pydantic/blob/master/examples/fastapi_example.py
    """

    #ipAddress = socket.gethostbyname(socket.gethostname())
    context = {"request": request, "name": welcomeXTerm, "ipAddress": ipAddress}
    return templates.TemplateResponse("general_pages/terminal.html", context)


@app.get("/interactiveGPIOPinout", response_class=HTMLResponse)
def interactiveGPIOP(request: Request):
    """
    An API endpoint that renders an interactive GPIO pinout HTML page.

    From the amazing website: https://pinout.xyz/

    Parameters:
        request (Request): The request object

    Returns:
        TemplateResponse: The HTML page with the GPIO pinout
    """

    #ipAddress = socket.gethostbyname(socket.gethostname())
    context = {"request": request, "name": interactiveGPIOPinout}
    return templates.TemplateResponse("general_pages/interactiveGPIOPinout.html", context)


'''
@app.post("/GPIO_Type_Input", response_model=List[GPIO])


@app.post("/GPIO_Type_Output", response_model=List[GPIO])


@app.post("/GPIO_State_Low", response_model=List[GPIO])


@app.post("/GPIO_State_High", response_model=List[GPIO])
'''