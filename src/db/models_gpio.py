from typing import Optional, List

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

class GPIOSelect(SQLModel):
    gpio: int = Field(index=True)


class pinSelect(SQLModel):
    pin: int = Field(index=True)

class GPIOBase(SQLModel):
    gpio: int = Field(index=True)
    pin: int
    name: str
    type: str
    state: str
    usedfor: Optional[str] = None
    changed: str


# Once the child model GPIO (the actual table model) inherits those fields
# from class GPIOBase, it will use those field configurations
# to create the indexes when creating the tables in the database.if that is called for
class GPIO(GPIOBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# The fields we need to create are exactly the same as the ones in the GPIOBase model.
# So we don't have to add anything.
# On top of that, we could easily decide in the future that we want to receive more data
# when creating a new GPIO apart from the data in GPIOBase (for example, a password),
# and now we already have the class to put those extra fields.
class GPIOCreate(GPIOBase):
    pass


class GPIORead(GPIOBase):
    id: int


class GPIOUpdate(SQLModel):
    gpio: Optional[int] = None
    pin: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None
    state: Optional[str] = None
    changed: Optional[str] = None
    usedfor: Optional[str] = None

'''
Inheritence Notes:

Only inherit from data models, don't inherit from table models.

It will help you avoid confusion, and there won't be any reason for you to need to inherit from a table model.

If you feel like you need to inherit from a table model, then instead create a base class that is only a data model 
and has all those fields, like GPIOBase.

And then inherit from that base class that is only a data model for any other data model and for the table model.

If you see you have a lot of overlap between two models, then you can probably avoid some of that duplication 
with a base model.

Main Points Recap:

You can use SQLModel to declare multiple models:

Some models can be only data models. They will also be Pydantic models.
And some can also be table models (apart from already being data models) by having the config table = True. 
They will also be Pydantic models and SQLAlchemy models.
Only the table models will create tables in the database.
'''