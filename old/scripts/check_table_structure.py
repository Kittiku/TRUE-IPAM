import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost', 
        user='root', 
        password='9371', 
        database='ipam_db'
    )
    cursor = conn.cursor()
    
    # Check table structure
    cursor.execute("DESCRIBE ip_inventory")
    columns = cursor.fetchall()
    print("Table structure:")
    for col in columns:
        print(f"  {col[0]} - {col[1]} ({col[2]})")
    
    print("\n" + "="*50)
    
    # Check sample data
    cursor.execute('SELECT COUNT(*) FROM ip_inventory')
    total_count = cursor.fetchone()[0]
    print(f'Total records: {total_count}')
    
    if total_count > 0:
        cursor.execute('SELECT * FROM ip_inventory LIMIT 3')
        sample_data = cursor.fetchall()
        print(f'\nSample data (first 3 records):')
        for row in sample_data:
            print(f"  {row}")
    
    conn.close()
    
except mysql.connector.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Error: {e}")
