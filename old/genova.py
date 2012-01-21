#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008 Stefano Costa, ominiverdi
# Filename: aria.py

# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import psycopg2
import re

from BeautifulSoup import BeautifulSoup
from datetime import date, timedelta


ariaHtml = open("Tabulatos.html").read()
ariaSoup = BeautifulSoup(ariaHtml)

h24 = timedelta(1)
today = date.today()
yesterday =  date.isoformat(today - h24)
periodo = ariaSoup.findAll(text=re.compile('Periodo di osservazione'))[0].string
parole = re.split('\W+', periodo)
yesterdayz = (parole[7], parole[8], parole[9])
todayz = (parole[14], parole[15], parole[16])

mesi = { 'gennaio' : 1,
    'febbraio' : 2,
    'marzo' : '03',
    'aprile' : '04',
    'maggio' : '05',
    'giugno' : '06',
    'luglio' : '07',
    'agosto' : '08',
    'settembre' : '09',
    'ottobre' : '10',
    'novembre' : '11',
    'dicembre' : '12'
}

if yesterdayz[1] in mesi:
  mese = mesi[yesterdayz[1]]

print mese
yesdate = "%s-%s-%s" % (yesterdayz[2], mese, yesterdayz[0])


print "\n"
print 'Periodo di osservazione:'
dalle = "dalle ore %s del %s" % (parole[5], yesdate)
print dalle
#print 'alle ore 8 del', today
print "\n"

DSN = "dbname='aria' user='air' host='localhost' password='CameraGas'"
conn = psycopg2.connect(DSN)


locations = { 'Giovi' : ['o3', 'no2'],
    'Acquasola': ['so2', 'co', 'o3', 'no2'],
    'Quarto': ['so2', 'co', 'o3', 'no2'],
    'Sestri Ponente': ['so2', 'co', 'no2'],
    'C.so Firenze': ['so2', 'co', 'no2'],
    'Villa Raggio': ['so2'],
    'Rimessa A.M.T.': ['so2'],
    'Calasanzio': ['so2'],
    'Corso Europa': ['co', 'no2'],
    'C.so Buenos Aires': ['co', 'no2'],
    'Gavette': ['so2', 'co', 'no2'],
    'P.zza Masnata': ['co', 'no2'],
    'Via Molteni': ['so2', 'co', 'no2'],
    'Via Buozzi': ['so2', 'co', 'no2'],
    'Via Pastorino' : [ 'co', 'no2'],
    'Montegrappa': ['co', 'no2'],
    'Giardini Melis': ['so2', 'co', 'no2'],
    'Multedo': ['so2', 'co', 'no2'],
    }

dataStore = []
note_dell_omino = re.compile(r"^\(.\)$")

for loc in locations:
    sensors = locations[loc]
    limit = len(sensors) * 3 - 2
    loc_in_html = ariaSoup.find(text=loc)
    if loc_in_html:
        measures = loc_in_html.findAllNext('b', limit=limit)
        indesex = 0
        for sex in sensors:
            indesex_iter = indesex + sensors.index(sex) * 3
            try:
                value = float(measures[indesex_iter].string)
            except:
                try:
                    note_dell_omino.search(measures[indesex_iter].string)
                except:
                    value = None
                else:
                    indesex = indesex - 2
            #print '\t', sex, ':', value
            dataStore.append((yesdate, loc, sex, value))
    else:
        print("La stazione %s oggi non ha valori" % loc)

#print dataStore

def insertIntoPg():
    '''Insert into the Postgres database the extracted values.'''
    c = conn.cursor()
    for rec in dataStore:
        c.execute('insert into tempgenova values (%s, %s, %s, %s)', rec)
    conn.commit()

    c = conn.cursor()
    whereCond = ('so2',)
    c.execute('select * from tempgenova where sensore=%s', whereCond)
    for row in c:
        print row
    
    file = open('/home/steko/log/aria.log', 'a')
    file.write(date.isoformat(date.today())+': retrieved data')
    file.close()

insertIntoPg()
