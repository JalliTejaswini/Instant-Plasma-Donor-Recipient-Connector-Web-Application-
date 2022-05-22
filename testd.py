import sqlite3
import string
from random import choices

char = string.ascii_letters + string.digits


def db_connect():
    conn = sqlite3.connect("plasma_donor.sqlite")
    cursor = conn.cursor()

    cursor.execute("""create table if not exists donor(id integer primary key autoincrement, username varchar(20), emailId varchar(40), password varchar(20), gender varchar(2), dob varchar(10), bgroup varchar(6), age varchar(3), contact varchar(14), address Text, cert Text)""")

    cursor.execute("""
        create table if not exists bbank (id integer primary key autoincrement, emailId varchar(20),password varchar(30))
                   """)

    cursor.execute("""
        create table if not exists bbank_donor_status (id integer primary key autoincrement, userId interger, status varchar(20))
        """)

    cursor.execute("""
                   create table if not exists blood_table (id integer primary key autoincrement, bgroup varchar(10), quantity integer)
                   """)
    
    
    cursor.execute('''
        create table if not exists hospital (id integer primary key autoincrement, h_name varchar(30), password varchar(30), address Text, contact varchar(20))
                   ''')
    
    cursor.execute('''
        create table if not exists hospital_req (id integer primary key,bgroup varchar(5),
        quantity integer, feedback text, status varchar(20), h_id integer)                   
                   ''')
    
    return cursor, conn.close, conn.commit


cursor, close, commit = db_connect()

cursor.execute(
    "insert into bbank (emailId,password) values('admin@mail.com', '1234567890')")


users = [("one", "one@mail.com", "qwerty", "1",
          "1998-01-10", "A+", 24, "1234567890", "dummy", "1_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("two", "two@mail.com", "qwerty", "1",
          "1998-01-10", "B+", 24, "1234567890", "dummy", "2_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("three", "three@mail.com", "qwerty", "1",
          "1998-01-10", ")+", 24, "1234567890", "dummy", "3_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("four", "four@mail.com", "qwerty", "1",
          "1998-01-10", "O-", 24, "1234567890", "dummy", "4_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("five", "five@mail.com", "qwerty", "1",
          "1998-01-10", "AB+", 24, "1234567890", "dummy", "5_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("six", "six@mail.com", "qwerty", "1",
          "1998-01-10", "AB-", 24, "1234567890", "dummy", "6_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("seven", "seven@mail.com", "qwerty", "1",
          "1998-01-10", "O-+", 24, "1234567890", "dummy", "7_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("eight", "eight@mail.com", "qwerty", "1",
          "1998-01-10", "A+", 24, "1234567890", "dummy", "8_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("nine", "nine@mail.com", "qwerty", "1",
          "1998-01-10", "B+", 24, "1234567890", "dummy", "9_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("ten", "ten@mail.com", "qwerty", "1",
          "1998-01-10", "AB+", 24, "1234567890", "dummy", "10_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("ele", "ele@mail.com", "qwerty", "1",
          "1998-01-10", "AB-", 24, "1234567890", "dummy", "11_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("twe", "one@mail.com", "qwerty", "1",
          "1998-01-10", "A+", 24, "1234567890", "dummy", "12_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ("thir", "thir@mail.com", "qwerty", "1",
          "1998-01-10", "B+", 24, "1234567890", "dummy", "13_ac9e561a87d6edcca8c9f4e8ae162982.jpg"),
         ]


status = [
    (1, "request"),
    (2, "request"),
    (3, "request"),
    (4, "request"),
    (5, "request"),
    (6, "request"),
    (7, "request"),
    (8, "request"),
    (9, "request"),
    (10, "request"),
    (11, "request"),
    (12, "request"),
    (13, "request"),
]


cursor.executemany(
    "insert into donor (username , emailId , password, gender , dob , bgroup , age , contact , address,cert ) values(? , ? , ?, ? , ? , ? , ? , ? , ?,?)", users)

cursor.executemany("insert into bbank_donor_status (userId, status)values(?,?)", status)

commit()
close()
