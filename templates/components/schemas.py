from fastapi import Form, File, UploadFile
from pydantic import BaseModel

# https://stackoverflow.com/a/60670614
class GPIOForm(BaseModel):
    gpio: int
    type: str
    state: str
    usedfor: str

    @classmethod
    def as_form(
            cls,
            gpio: int = Form(...),
            type: str = Form(...),
            state: str = Form(...),
            usedfor: str = Form(...)
    ):
        return cls(
            gpio=gpio,
            type=type,
            state=state,
            usedfor=usedfor
        )


class idForm(BaseModel):
    gpio: int
#    name: str
#    type: str
#    state: str

    @classmethod
    def as_form(
        cls,
        gpio: int = Form(...),  # The GPIO pin number
            # name: str = Form(...),  # The name of the pin
            # type: str = Form(...),  # The type of the pin
            # state: str = Form(...)  # The state of the pin
    ) -> 'ClassName':
        """Create an instance of the class from form data."""
        return cls(
            gpio=gpio,
            # name=name,
            # type=type,
            # state=state
        )


class initializationForm(BaseModel):
    username: str
    password : str

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
    ):
      return cls(
          username=username,
          password=password,
      )


class LoginForm(BaseModel):
    username: str
    password : str
    file: UploadFile

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
        file: UploadFile = File(...)
    ):
      return cls(
          username=username,
          password=password,
          file=file
      )