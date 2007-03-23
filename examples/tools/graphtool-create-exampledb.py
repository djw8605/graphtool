#!/usr/bin/env python

from pysqlite2 import dbapi2 as sqlite
import time
import random
import os
import math

con = sqlite.connect(os.environ["GRAPHTOOL_USER_ROOT"]+"/example.db")
cur = con.cursor()

cur.execute('''create table pirate (id INTEGER, name varchar(100) ) ''')
cur.execute('''create table treasure (timebin integer, pirate integer, gold integer, jewels integer)''')

pirates = ({ 'id': 0, 'name': 'Shoutin Clive Morgan' },
           { 'id': 1, 'name': 'Screaming Sam'},
           { 'id': 2, 'name': 'Bluebeard'},
           { 'id': 3, 'name': 'Hairy Jock Smythe' },
           { 'id': 4, 'name': 'Pele' },
           { 'id': 5, 'name': 'Leather-face John Blackbeard' },
           { 'id': 6, 'name': 'Sir William Defoe' })

insert = '''insert into pirate (id, name) values (:id, :name)'''
for pirate in pirates:
    cur.execute(insert, pirate)

insert = '''insert into treasure (timebin, pirate, gold, jewels) values (:timebin, :pirate, :gold, :jewels)'''

t_end = time.time()
t = t_end - 365*24*3600
while t < t_end:
    for pirate in pirates:
        gold = 100 * random.random()
        jewels = int(math.floor(100 * random.random()))
        binds = { 'timebin': t, 'pirate': pirate['id'], 'gold': gold, 'jewels': jewels }
        print "At %s pirate %s got %s gold and %s jewels" % (t, pirate, gold, jewels)
        cur.execute(insert, binds)
    t += 24*3600

con.commit()
