# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from peewee import Model
from peewee import CharField
from database import db
from database import AbstractModel

class Doda(AbstractModel):
    company_name = CharField()
    url_doda = CharField()
    postal_code = CharField(null=True)
    address = CharField(null=True)
    TEL = CharField(null=True)
    remarks = CharField(null=True)
    url_company = CharField(null=True)

    class Meta:
        db_table = 'doda'


def main():
    if not db.table_exists("doda"):
    # if not Doda.table_exists():
        db.create_tables([Doda])


if __name__ == "__main__":
    main()
