#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import pymysql
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():

    db = pymysql.connect(
            host=os.environ.get('MYSQL_HOST'),
            user=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASSWORD'),
            db=os.environ.get('MYSQL_DATABASE'),
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
        )

    cur = db.cursor()
    sql = "select * from doda"
    cur.execute(sql)
    records = cur.fetchall()

    cur.close()
    db.close()

    return render_template('index.html', title='list of companies', records=records)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
