import pymysql

# Database connection helper module
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='ecommerce'
    )
