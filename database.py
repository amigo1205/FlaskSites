import os
import pymysql as sql
from config import app
import log



HOST = os.getenv('DB_HOST', 'localhost') # If running locally, probably need to override default.
USER = os.getenv('DB_USER', 'root')
PASS = os.getenv('DB_PASS', '')
DATABASE = os.getenv('DB_DATABASE', 'clickmd')



# USAGE:
# conn = database.connect()
# with conn.cursor() as cursor:
#     cursor.execute('CREATE TABLE test2 (name VARCHAR(20))')
#     conn.commit()
#     cursor.close()
# conn.close()
def connect(logErrors=True):
    db = None
    cursor = None

    try:
        db = sql.connect(host=HOST,
                    user=USER,
                    password=PASS,
                    db=DATABASE,
                    connect_timeout=15)
        cursor = db.cursor()
    except Exception as e:
        if logErrors:
            log.log.exception( e )
        return (None,None, str(e) )
    return ( db , cursor , "success")



app.config.from_object( __name__ )



