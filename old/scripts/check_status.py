#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

def check_status_data():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ipam_db',
            user='root',
            password='9371'
        )
        cursor = connection.cursor()
        
        print('=== Overall Status Distribution ===')
        cursor.execute('SELECT status, COUNT(*) as count FROM ip_inventory GROUP BY status ORDER BY count DESC')
        status_data = cursor.fetchall()
        total_records = sum(row[1] for row in status_data)
        print(f'Total Records: {total_records}')
        for row in status_data:
            percentage = (row[1] / total_records) * 100
            print(f'{row[0]}: {row[1]} ({percentage:.1f}%)')
        
        print('\n=== IPRAN-D Status Distribution ===')
        cursor.execute('SELECT status, COUNT(*) as count FROM ip_inventory WHERE vrf_vpn = "IPRAN-D" GROUP BY status ORDER BY count DESC')
        ipran_data = cursor.fetchall()
        ipran_total = sum(row[1] for row in ipran_data)
        print(f'IPRAN-D Total Records: {ipran_total}')
        for row in ipran_data:
            percentage = (row[1] / ipran_total) * 100
            print(f'{row[0]}: {row[1]} ({percentage:.1f}%)')
        
        print('\n=== IPRAN-D Sample Records ===')
        cursor.execute('SELECT ip_address, subnet, status, vrf_vpn FROM ip_inventory WHERE vrf_vpn = "IPRAN-D" LIMIT 5')
        sample_data = cursor.fetchall()
        for row in sample_data:
            print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]}')
        
        print('\n=== Check if status has unexpected values ===')
        cursor.execute('SELECT DISTINCT status FROM ip_inventory ORDER BY status')
        distinct_status = cursor.fetchall()
        print('Available status values:')
        for status in distinct_status:
            print(f'  - "{status[0]}"')
            
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f'Database Error: {e}')

if __name__ == '__main__':
    check_status_data()
