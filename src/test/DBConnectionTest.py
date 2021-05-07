from unittest.mock import patch, MagicMock


import unittest
from unittest import mock
from util import db_config

class Test_insert_rows(unittest.TestCase):

    def fix_dbc(self):
        dbc = mock.MagicMock(spec=['cursor'])
        dbc.autocommit = True
        return dbc

    def fix_rows(self):
        rows = [{'id':1, 'name':'John'}, 
                {'id':2, 'name':'Jane'},]
        return rows

    def test_insert_rows_calls_cursor_method(self):
        dbc = self.fix_dbc()
        rows = self.fix_rows()
        insert_rows(rows, 'users', dbc)
        self.assertTrue(dbc.cursor.called)

    def test(self, mock_sql):
        self.assertIs(mypackage.mymodule.pymysql, mock_sql)

        conn = Mock()
        mock_sql.connect.return_value = conn

        cursor      = MagicMock()
        mock_result = MagicMock()

        cursor.__enter__.return_value = mock_result
        cursor.__exit___              = MagicMock()

        conn.cursor.return_value = cursor

        connectDB()

        mock_sql.connect.assert_called_with(host=db_config['host'],
                                            user=db_config['user'],
                                            password=db_config['password'],
                                            db=db_config['database'])

        mock_result.execute.assert_called_with("sql request", ("user", "pass"))
    
    def fix_tuples(self):
        tuples = [(1,'John'),
                  (2,'Jane'),]
        return tuples

    def test_insert_rows_calls_executemany_and_commit_passing_correct_arguments(self):
        dbc = self.fix_dbc()
        rows = self.fix_rows()

        insert_rows(rows, 'users', dbc)

        with dbc.cursor() as cursor:
            expect_sql = 'INSERT INTO users(id, name) VALUES (?,?)'
            expect_tuples = self.fix_tuples()
            calls = [mock.call.executemany(expect_sql, expect_tuples),
                     mock.call.commit(),]
            cursor.assert_has_calls(calls)
        self.assertTrue(dbc.autocommit)

    def test_insert_rows_rollsback_transaction_on_databse_exception(self):
        dbc = self.fix_dbc()
        rows = self.fix_rows()

        with dbc.cursor() as cursor:
            cursor.executemany.side_effect = Exception('Some DB error')

            with self.assertRaises(Exception) as exc:
                insert_rows(rows, 'users', dbc)

            calls = [mock.call.executemany(mock.ANY, mock.ANY),
                     mock.call.rollback(),]
            cursor.assert_has_calls(calls)
        self.assertTrue(dbc.autocommit)
        self.assertEqual('Some DB error', str(exc.exception))

    def insert_rows(rows, table_name, dbc):
        field_names = rows[0].keys()
        field_names_str = ', '.join(field_names)
        placeholder_str = ','.join('?'*len(field_names))
        insert_sql = f'INSERT INTO {table_name}({field_names_str}) VALUES ({placeholder_str})'
        saved_autocommit = dbc.autocommit
        with dbc.cursor() as cursor:
            try:
                dbc.autocommit = False
                tuples = [ tuple((row[field_name] for field_name in field_names)) for row in rows ]
                cursor.executemany(insert_sql, tuples)
                cursor.commit()
            except Exception as exc:
                cursor.rollback()
                raise exc
            finally:
                dbc.autocommit = saved_autocommit    


if __name__ == '__main__':
    unittest.main(argv=['', '-v'])

