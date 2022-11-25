import logging
import sqlite3

from config import Contact, Program, Specialization, Institution, Profession


def connect_to_db(db_name):
    db = sqlite3.connect(f"{db_name}.db")
    cursor = db.cursor()
    return db, cursor


def create_table_for_institution(db_name: str):
    db, cursor = connect_to_db(db_name)
    cursor.execute("""CREATE TABLE IF NOT EXISTS institution(
        institutionID VARCHAR(50),
        name TEXT,
        description TEXT,
        img TEXT,
        logo TEXT,
        cost INTEGER,
        budget_places INTEGER,
        payment_places INTEGER,
        budget_points FLOAT,
        payment_points FLOAT,
        url TEXT
    )""")
    db.commit()
    db.close()

def create_table_for_contacts(db_name: str):
    db, cursor = connect_to_db(db_name)
    cursor.execute("""CREATE TABLE IF NOT EXISTS contact(
        contactID INTEGER PRIMARY KEY AUTOINCREMENT,
        website VARCHAR(100),
        email VARCHAR(100),
        phones VARCHAR(100),
        address TEXT,
        institutionID VARCHAR(50) REFERENCES institution(institutionID)
    )""")
    db.commit()
    db.close()

def create_table_for_specialization(db_name: str):
    db, cursor = connect_to_db(db_name)
    cursor.execute("""CREATE TABLE IF NOT EXISTS specialization(
        specID VARCHAR(20),
        institutionID VARCHAR(30) REFERENCES institution(institutionID),
        name TEXT,
        description TEXT,
        direction TEXT,
        img TEXT,
        cost INTEGER,
        budget_places INTEGER,
        payment_places INTEGER,
        budget_points FLOAT,
        payment_points FLOAT,
        url TEXT
    )""")
    db.commit()
    db.close()

def create_table_for_programs(db_name: str):
    db, cursor = connect_to_db(db_name)
    cursor.execute("""CREATE TABLE IF NOT EXISTS program(
        programID INTEGER,
        specID INTEGER REFERENCES specialization(specID),
        institutionID VARCHAR(50) REFERENCES institution(institutionID),
        name TEXT,
        description TEXT,
        direction TEXT,
        form VARCHAR(50),
        img TEXT,
        cost INTEGER,
        budget_places INTEGER,
        payment_places INTEGER,
        budget_points FLOAT,
        payment_points FLOAT,
        subjects VARCHAR(255),
        url TEXT
    )""")
    db.commit()
    db.close()

def create_table_for_profession(db_name: str):
    db, cursor = connect_to_db(db_name)
    cursor.execute("""CREATE TABLE IF NOT EXISTS profession(
        professionID INTEGER PRIMARY KEY AUTOINCREMENT,
        programID INTEGER REFERENCES program(programID),
        name TEXT,
        img TEXT
    )""")
    db.commit()
    db.close()



def add_institution(data:Institution, db_name: str = ""):
    create_table_for_institution(db_name)
    db, cursor = connect_to_db(db_name)
    cursor.execute(f"INSERT INTO institution(institutionID, name , description, img, logo, cost, budget_places, payment_places, budget_points ,payment_points, url) VALUES({','.join(['?' for i in data])})", tuple(data))
    db.commit()
    db.close()

def add_spec(data:Specialization, db_name: str = ""):
    create_table_for_specialization(db_name)
    db, cursor = connect_to_db(db_name)
    cursor.execute(f"INSERT INTO specialization(specID, institutionID, name , description, direction, img, cost, budget_places, payment_places, budget_points ,payment_points, url) VALUES({','.join(['?' for i in data])})", tuple(data))
    db.commit()
    db.close()



def add_contact(data:Contact, db_name: str = ""):
    create_table_for_contacts(db_name)
    db, cursor = connect_to_db(db_name)
    cursor.execute(f"INSERT INTO contact(website, email, phones, address, institutionID) VALUES({','.join(['?' for i in data])})", tuple(data))
    db.commit()
    db.close() 


def add_program(data:Program, db_name: str = ""):
    create_table_for_programs(db_name)
    db, cursor = connect_to_db(db_name)
    cursor.execute(f"INSERT INTO program(programID, specID, institutionID, name, description, direction, form, img, cost, budget_places, payment_places, budget_points ,payment_points, subjects, url) VALUES({','.join(['?' for i in data])})", tuple(data))
    db.commit()
    db.close()


def add_profession(data:Profession, db_name: str = ""):
    create_table_for_profession(db_name)
    db, cursor = connect_to_db(db_name)
    cursor.execute(f"INSERT INTO profession(programID, name, img) VALUES({','.join(['?' for i in data])})", tuple(data))
    db.commit()
    db.close()


if __name__ == "__main__":
    add_institution(data=['kfe', 'dedefdeadeadeadea', 'deadsdasdasdas', 'vdsasadasdas', 123232, 12, 314, 1.4, 4.5])
    add_spec(data=['kfe', 'dedefdeadeadeadea', 'deadsdasdasdas', 'vdsasadasdas', 123232, 12, 314, 1.4, 4.5])
