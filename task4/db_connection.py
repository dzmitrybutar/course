from mysql.connector import MySQLConnection


class Connection:
    """Base class to connect to the database."""

    def __init__(self, db_config: dict, **kwargs):
        self.db_config = db_config
        self.cursor_param = kwargs
        self.cursor = None


class MysqlConnection(Connection):
    """Class to connect to the MySQL database."""

    def __enter__(self):
        self.connection = MySQLConnection(**self.db_config)
        if not self.cursor_param:
            self.cursor = self.connection.cursor()
        else:
            self.cursor = self.connection.cursor(**self.cursor_param)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()


