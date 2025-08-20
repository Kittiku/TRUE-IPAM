import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost', 
        user='root', 
        password='9371', 
        database='ipam_db'
    )
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM ip_inventory')
    total_count = cursor.fetchone()[0]
    print(f'Total records: {total_count}')
    
    if total_count > 0:
        cursor.execute('SELECT COUNT(*) FROM ip_inventory WHERE vrf_vpn IS NOT NULL AND vrf_vpn != ""')
        vrf_count = cursor.fetchone()[0]
        print(f'Records with VRF/VPN: {vrf_count}')
        
        cursor.execute('SELECT DISTINCT vrf_vpn FROM ip_inventory WHERE vrf_vpn IS NOT NULL AND vrf_vpn != "" LIMIT 5')
        vrf_samples = cursor.fetchall()
        print(f'Sample VRF/VPN values: {[v[0] for v in vrf_samples]}')
    else:
        print('No data found in ip_inventory table')
    
    conn.close()
    
except mysql.connector.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Error: {e}")
