# !/usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import *
db = MySQLDatabase(
  'recruit',
  **{'user': 'root',
     'host': '172.29.0.2',
     'password': 'root'}
)
db.connect()