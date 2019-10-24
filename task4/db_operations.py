from mysql.connector import Error
from db_connection import MysqlConnection


class MysqlExecutor:
    """Class for working with MySQL the database."""

    def __init__(self, db_config: dict):
        self.db_config = db_config

    def insert(self, data: list, fields: list, table: str):
        """Writing data to the database"""

        try:
            with MysqlConnection(self.db_config) as db:
                query = "INSERT IGNORE INTO {} ({}) values ({})".format(
                    table, ",".join(fields), ",".join(['%s'] * len(fields)))
                db.cursor.executemany(query, data)

        except Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def select(self, query: str):
        """Database query for data."""

        try:
            with MysqlConnection(self.db_config) as db:
                db.cursor.execute(query)
                records = db.cursor.fetchall()
                return records

        except Error as error:
            print("Failed to select into MySQL table {}".format(error))
