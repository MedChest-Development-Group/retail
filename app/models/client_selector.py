from collections.abc import Mapping, Sequence
from typing import Any
from wtforms import Form, SelectField


class ClientSelector(Form):
    clients = SelectField(u'', choices=[])