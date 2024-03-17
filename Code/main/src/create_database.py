import mysql.connector
import pandas as pd
import configparser

# Connect to MySQL
config = configparser.ConfigParser()
config.read("Lab4.conf")

conn = mysql.connector.connect(
    host=config['MySQL']['host'],
    user=config['MySQL']['user'],
    password=config['MySQL']['password']
)
cursor = conn.cursor()

# Create dsci560 database
cursor.execute("CREATE DATABASE IF NOT EXISTS chatbot")

# Using dsci560 database
cursor.execute("USE chatbot")

# Create reddit table
cursor.execute("DROP TABLE IF EXISTS user")
cursor.execute("""

CREATE TABLE user (
    id VARCHAR(36) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    age INT,
    gender VARCHAR(50),
    food VARCHAR(255),
    allergen VARCHAR(255),
    PRIMARY KEY (id),
    UNIQUE (username)
);

""")


conn.commit()

cursor.close()
conn.close()
