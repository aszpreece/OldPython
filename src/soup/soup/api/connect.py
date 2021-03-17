import mariadb
import sys


def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mariadb.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MariabDB SQL Database connection successful")
    except mariadb.Error as err:
        print(f"Error: '{err}'")

    return connection