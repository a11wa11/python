# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime

from peewee import Model
from peewee import MySQLDatabase
from peewee import DateTimeField

# 接続方法１
# db = MySQLDatabase(
#   database = 'database_name',
#   host = 'host_name',
#   user = 'user_name',
#   password = 'password'
#   port = 3306,
#   charset = "utf8mb4"
# )

# db = MySQLDatabase(
#   database = os.environ.get('MYSQL_DATABASE'),
#   host = os.environ.get('MYSQL_HOST'),
#   user = os.environ.get('MYSQL_USER'),
#   password = os.environ.get('MYSQL_PASSWORD')
# )

# 接続方法2 -> db = connect('mysql://user:password@ip:port/my_db')
from playhouse.db_url import connect
db = connect(os.environ.get('DATABASE_URL'))


class AbstractModel(Model):
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    class Meta:
        database = db
