#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
import ipaddress
import random

def fix_ip_status():
    """Fix IP status to be more realistic - not all IPs in a subnet should be 'used'"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ipam_db',
            user='root',
            password='9371'
        )
        cursor = connection.cursor()
        
        print('🔧 Fixing IP status to be more realistic...')
        
        # Get all unique subnets
        cursor.execute('SELECT DISTINCT subnet FROM ip_inventory ORDER BY subnet')
        subnets = cursor.fetchall()
        
        total_updated = 0
        
        for subnet_row in subnets:
            subnet = subnet_row[0]
            try:
                # Parse subnet to get all possible IPs
                network = ipaddress.IPv4Network(subnet, strict=False)
                total_possible_ips = network.num_addresses - 2  # Exclude network and broadcast
                
                # Get current IPs in this subnet
                cursor.execute('SELECT COUNT(*) FROM ip_inventory WHERE subnet = %s', (subnet,))
                current_ips = cursor.fetchone()[0]
                
                # Calculate realistic usage (typically 20-80% of available IPs)
                usage_percent = random.randint(20, 80)
                target_used_ips = max(1, int(current_ips * usage_percent / 100))
                
                # Get all IPs in this subnet
                cursor.execute('SELECT id FROM ip_inventory WHERE subnet = %s ORDER BY RAND()', (subnet,))
                ip_ids = cursor.fetchall()
                
                # Set some as available, some as reserved
                for i, ip_id in enumerate(ip_ids):
                    if i < target_used_ips:
                        new_status = 'used'
                    elif i < target_used_ips + max(1, int(current_ips * 0.1)):  # 10% reserved
                        new_status = 'reserved'
                    else:
                        new_status = 'available'
                    
                    cursor.execute('UPDATE ip_inventory SET status = %s WHERE id = %s', (new_status, ip_id[0]))
                    total_updated += 1
                
                if total_updated % 1000 == 0:
                    print(f'  Updated {total_updated} records...')
                    connection.commit()
                    
            except Exception as e:
                print(f'  Warning: Could not process subnet {subnet}: {e}')
                continue
        
        connection.commit()
        print(f'✅ Successfully updated {total_updated} IP records with realistic status')
        
        # Show new distribution
        print('\n=== New Status Distribution ===')
        cursor.execute('SELECT status, COUNT(*) as count FROM ip_inventory GROUP BY status ORDER BY count DESC')
        status_data = cursor.fetchall()
        total_records = sum(row[1] for row in status_data)
        
        for row in status_data:
            percentage = (row[1] / total_records) * 100
            print(f'{row[0]}: {row[1]} ({percentage:.1f}%)')
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f'❌ Database Error: {e}')

if __name__ == '__main__':
    fix_ip_status()
