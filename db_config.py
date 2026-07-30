import pymysql

# Database connection helper module
try:
    def get_db_connection():
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='ecommerce'
        )
except exception as e:
    print(e)
