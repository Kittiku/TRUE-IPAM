import mysql.connector

connection = mysql.connector.connect(
    host='localhost',
    database='ipam_db', 
    user='root',
    password='9371'
)
cursor = connection.cursor()

print('=== Subnet Distribution ===')
cursor.execute('SELECT subnet, COUNT(*) as count FROM ip_inventory GROUP BY subnet ORDER BY count DESC LIMIT 10')
subnet_data = cursor.fetchall()
for row in subnet_data:
    print(f'{row[0]}: {row[1]} IPs')

print('\n=== IPRAN-D Subnet Details ===')
cursor.execute('SELECT subnet, COUNT(*) as count FROM ip_inventory WHERE vrf_vpn = "IPRAN-D" GROUP BY subnet ORDER BY count DESC')
ipran_subnets = cursor.fetchall()
for row in ipran_subnets:
    print(f'{row[0]}: {row[1]} IPs')
    
cursor.close()
connection.close()
