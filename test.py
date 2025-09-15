import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=EMPLOYEE;"
    "UID=sa;"
    "PWD=test123;"
)

try:
    conn = pyodbc.connect(conn_str, timeout=5)
    print("Connected!")
except Exception as e:
    print("Connection error:", e)
