import mysql.connector

# Database connection parameters
db_config = {
    'user': 'root',
    'password': 'nb_r00t@20_24',
    'host': 'localhost',
    'database': 'stethona',
    'port': 3306
}

# Connect to the database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

query = "Select id from patients w"