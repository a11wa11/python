# !/usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import *
db = MySQLDatabase(
  'recruit',
  **{'user': 'root',
     'host': 'con_db',
     'password': 'root'}
)
db.connect()
db.close()
