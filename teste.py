import pyodbc 
conn = pyodbc.connect(
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=;suportedl.no-ip.org\nero"
    "Database=BILLS;"
    "Trusted_Connection=yes;"
)

print(conn)

cursor = conn.cursor()