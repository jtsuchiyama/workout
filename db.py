import psycopg2
from loguru import logger

class Database:
    """PostgreSQL Database class."""

    def __init__(self):
        self.host = "localhost"
        self.username = "postgres"
        self.password = "poke3271"
        self.port = 5432
        self.dbname = "Exercise"
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to a Postgres database."""
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    port=self.port,
                    dbname=self.dbname
                )
            except psycopg2.DatabaseError as e:
                logger.error(e)
                raise e
            finally:
                logger.info('Connection opened successfully.')

        

    def select(self, query):
        """Run a SQL query to select the data from a table."""
        with self.conn.cursor() as cur:
            cur.execute(query)
            records = [row for row in cur.fetchall()]
            cur.close()
            return records

    def add(self, query, values):
        """Run a SQL query to add a row in a table."""
        with self.conn.cursor() as cur:
            cur.execute(query, values)
            self.conn.commit()
            cur.close()
            return f"{cur.rowcount} rows affected."

    def delete(self, query):
        """Run a SQL query to delete a row in a table."""
        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()
            cur.close()
            return f"{cur.rowcount} rows affected."

    def update(self, query, values):
        """Run a SQL query to update a row in a table."""
        with self.conn.cursor() as cur:
            cur.execute(query, values)
            self.conn.commit()
            cur.close()
            return f"{cur.rowcount} rows affected."


