import pymysql
from datetime import datetime
import os
from typing import List, Dict, Set, Tuple


class MySqlInterface:
    connection: pymysql.connections.Connection
    enable_writes = True
    last_query = "NONE"

    def __init__(self, user_name: str, db_name: str, user_password: str = None, enable_writes: bool = True):
        # print("initializing")
        if user_password == None:
            user_password = os.environ.get("LOCAL_ROOT_MYSQL")

        self.enable_writes = enable_writes
        self.connection = pymysql.connect(
            host='localhost', user=user_name, password=user_password, db=db_name,
            cursorclass=pymysql.cursors.DictCursor, charset='utf8mb4')
        self.connection.autocommit(True)

    def set_enable_writes(self, val:bool):
        self.enable_writes = val

    def read_data(self, sql_str: str, tvals:Tuple = None, debug:bool = False) -> List:

        self.last_query = sql_str
        with self.connection.cursor() as cursor:
            if tvals == None:
                if debug:
                    print("MySqlInterface:\n\tquery = {}",format(sql_str))
                cursor.execute(sql_str)
            else:
                if debug:
                    print("MySqlInterface:\n\tquery = {}\n\tdata = {}".format(sql_str, tvals))
                cursor.execute(sql_str, tvals)
            result = cursor.fetchall()
            return result

    def write_data(self, sql_str: str):
        self.last_query = sql_str
        if not self.enable_writes:
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql_str)
        except pymysql.err.ProgrammingError as e:
            print(e)

    def write_data_get_row_id(self, sql_str: str) -> int:
        self.last_query = sql_str
        if not self.enable_writes:
            return -1

        with self.connection.cursor() as cursor:
            # print(sql_str)
            cursor.execute(sql_str)
            return cursor.lastrowid

    # see https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html
    def write_sql_values_get_row(self, sql:str, values:Tuple, debug:bool=False):
        if not self.enable_writes:
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, values)
                id = cursor.lastrowid
                if debug:
                    print("row id = {}".format(id))
                return id
        except pymysql.err.InternalError as e:
            print("{}:\n\t{}".format(e, sql))
            return -1

    def escape_text(self, to_escape):
        if type(to_escape) is str:
            return self.connection.escape(to_escape)

        return to_escape

    def get_last_query(self) -> str:
        return self.last_query

    def close(self):
        self.connection.close()


if __name__ == '__main__':
    msi = MySqlInterface("root", "gpt_summary")
    sql = "describe table_parsed_text"
    result = msi.read_data(sql)
    for d in result:
        print(d)
    msi.close()

'''
Create a list of all words
Create a timeline of all words
Plot that and see if any patterns present themselves
'''
