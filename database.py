import psycopg2

def connect_to_database():
    try:
        connection=psycopg2.connect(
            host='localhost',
            port='3000',
            database='BankSystem',
            user='postgres',
            password='pass'
        )

        print("Connection Succesufull...")
        return connection
    
    except Exception as error:
        print("Error In Database",error)
        return None


if __name__=="__main__":
    conn=connect_to_database()
    if conn:
        conn.close()
        print("Connection closed!")

    