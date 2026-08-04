import pymysql

# XAMPP MySQL Database Connection Function
def get_db_connection():
    try:
        # XAMPP MySQL credentials (host: localhost, user: root, password: '')
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='ecommerce',
            autocommit=True
        )
        return connection
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None
