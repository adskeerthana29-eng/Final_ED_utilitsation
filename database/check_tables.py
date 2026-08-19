import sqlite3

conn = sqlite3.connect("ed_utilization.db")
cursor = conn.cursor()

# ======================================
# Show all tables
# ======================================

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name
""")

tables = cursor.fetchall()

print("\nTables in Database:")
for table in tables:
    print("-", table[0])

print("\n=====================================")

# ======================================
# EHR Historical Data
# ======================================

cursor.execute("SELECT COUNT(*) FROM ehr_historical_data")
historical_count = cursor.fetchone()[0]

print("EHR Historical Records :", historical_count)

print("\nFirst 5 Historical Records\n")

cursor.execute("""
SELECT *
FROM ehr_historical_data
LIMIT 5
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

print("\n=====================================")

# ======================================
# Current Patient Data
# ======================================

cursor.execute("SELECT COUNT(*) FROM current_patient_data")
current_count = cursor.fetchone()[0]

print("Current Patient Records :", current_count)

print("\nLatest Current Patient Records\n")

cursor.execute("""
SELECT *
FROM current_patient_data
ORDER BY rowid DESC
LIMIT 5
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()

print("\nDatabase verification completed successfully.")