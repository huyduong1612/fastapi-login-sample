import psycopg2
import pandas as pd


class BaseService:
    def __init__(self, connection):
        self.connection = connection

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params)
            self.connection.commit()
        except psycopg2.Error as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def check_function_return_type(self, proc_name) -> str:
        cursor = self.connection.cursor()

        try:
            query = """
                SELECT p.proname AS function_name, pg_catalog.format_type(p.prorettype, NULL) AS return_type
                FROM pg_catalog.pg_proc p
                LEFT JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
                WHERE p.proname = %s
                AND n.nspname = %s
            """
            cursor.execute(query, (proc_name, 'public'))

            # Fetch the result
            result = cursor.fetchone()
            function_name, return_type = result

            return return_type
        except psycopg2.Error as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def execute_dataframe(self, query, params=None) -> pd.DataFrame:
        cursor = self.connection.cursor()

        try:

            cursor.execute(query, params)
            result = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(result, columns=column_names)
            self.connection.commit()
            return df
        except psycopg2.Error as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def callproc_dataframe(self, query, params=None) -> pd.DataFrame:
        cursor = self.connection.cursor()

        try:

            cursor.callproc(query, params)

            if (self.check_function_return_type(query) == 'refcursor'):
                _result = cursor.fetchone()[0]
                cursor.execute(f'FETCH ALL IN "{_result}"')
                result = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(result, columns=column_names)
            else:
                result = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(result, columns=column_names)

            self.connection.commit()
            return df
        except psycopg2.Error as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()
