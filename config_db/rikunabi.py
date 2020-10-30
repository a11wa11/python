# !/usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import CharField
from peewee import TextField

from config_db.database import AbstractModel

class Rikunabi(AbstractModel):
    company_name = CharField()
    url_rikunabi = CharField()
    postal_code = CharField(null=True)
    address = CharField(null=True)
    TEL = CharField(null=True)
    remarks = TextField(null=True)
    url_company = CharField(null=True)

    class Meta:
        db_table = 'rikunabi'
