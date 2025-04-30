import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",              # Change this if your MySQL username is different
        password="root",              # Add your MySQL password if you set one
        database="EventBookingPlatform"
    )
