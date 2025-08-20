#!/usr/bin/env python3
"""
Enhanced IPAM CSV Import Tool
Imports network inventory data with service domains and interface information
Prepares structure for actual VPN/VRF data integration
"""

import csv
import ipaddress
import re
from mysql_manager_enhanced import MySQLManager

def extract_vrf_from_description(description, interface_name):
    """
    Extract VRF information from interface description or name
    This is a placeholder - replace with actual VRF identification logic
    """
    if not description:
        return None
    
    # Common VRF patterns in descriptions
    vrf_patterns = [
        r'VRF[_-]?(\w+)',
        r'VPN[_-]?(\w+)', 
        r'RD[_-]?(\d+:\d+)',
        r'RT[_-]?(\d+:\d+)',
        r'MPLS[_-]?(\w+)'
    ]
    
    for pattern in vrf_patterns:
        match = re.search(pattern, description.upper())
        if match:
            return f"VRF_{match.group(1)}"
    
    # Check interface name for VRF indicators
    if interface_name:
        if 'vpn' in interface_name.lower():
            return f"VPN_{interface_name.split('vpn')[-1]}"
        if 'vrf' in interface_name.lower():
            return f"VRF_{interface_name.split('vrf')[-1]}"
    
    return None

def calculate_subnet(ip_str, default_prefix=24):
    """Calculate subnet from IP address"""
    try:
        ip = ipaddress.IPv4Address(ip_str)
        
        # Try to determine subnet based on IP class and common patterns
        if ip.is_private:
            if str(ip).startswith('10.'):
                prefix = 16  # Common for 10.x networks
            elif str(ip).startswith('192.168.'):
                prefix = 24  # Common for 192.168.x networks  
            elif str(ip).startswith('172.'):
                prefix = 20  # Common for 172.16-31 networks
            else:
                prefix = default_prefix
        else:
            prefix = default_prefix
            
        network = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
        return str(network)
        
    except (ipaddress.AddressValueError, ValueError):
        return None

def import_csv_data(csv_file='datalake.Inventory.port.csv', limit=None):
    """Import network inventory data from CSV"""
    
    print("🚀 Enhanced IPAM CSV Import Tool")
    print("=" * 80)
    
    # Initialize database connection (using direct MySQL connection like main_server.py)
    try:
        import mysql.connector
        from mysql.connector import Error
        
        connection = mysql.connector.connect(
            host='localhost',
            database='ipam_db',
            user='root',
            password='9371',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL database")
            
            # Update table structure to include new fields
            try:
                cursor = connection.cursor()
                
                # Add new columns if they don't exist
                alter_queries = [
                    "ALTER TABLE ip_inventory ADD COLUMN IF NOT EXISTS service_domain VARCHAR(100)",
                    "ALTER TABLE ip_inventory ADD COLUMN IF NOT EXISTS interface_name VARCHAR(100)",
                    "ALTER TABLE ip_inventory ADD COLUMN IF NOT EXISTS interface_desc VARCHAR(255)",
                    "ALTER TABLE ip_inventory ADD COLUMN IF NOT EXISTS interface_type VARCHAR(50)",
                    "ALTER TABLE ip_inventory ADD COLUMN IF NOT EXISTS vendor VARCHAR(100)",
                    "ALTER TABLE ip_inventory ADD COLUMN IF NOT EXISTS device_model VARCHAR(100)",
                    "ALTER TABLE ip_inventory ADD COLUMN IF NOT EXISTS admin_status VARCHAR(20)",
                    "ALTER TABLE ip_inventory ADD COLUMN IF NOT EXISTS oper_status VARCHAR(20)"
                ]
                
                for query in alter_queries:
                    try:
                        cursor.execute(query)
                        connection.commit()
                    except Error as e:
                        if "Duplicate column name" not in str(e):
                            print(f"⚠️ Warning: {e}")
                
                cursor.close()
                print("✅ Database structure updated")
                
            except Error as e:
                print(f"⚠️ Warning updating table structure: {e}")
        else:
            print("❌ Failed to connect to database")
            return False
            
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    # Analyze CSV structure
    print(f"🔍 Analyzing CSV structure: {csv_file}")
    print("=" * 80)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            
            print(f"📋 Headers ({len(headers)} columns):")
            for i, header in enumerate(headers, 1):
                print(f"    {i:2d}. {header}")
            
            # Show sample data
            print("\n📊 Sample data:")
            print("-" * 80)
            
            sample_rows = []
            for i in range(5):
                try:
                    row = next(reader)
                    sample_rows.append(row)
                except StopIteration:
                    break
            
            # Show meaningful sample data
            for i, row in enumerate(sample_rows, 1):
                print(f"\nRow {i}:")
                row_data = dict(zip(headers, row))
                for key in ['ifIP', 'host_name', 'ifName', 'ifDescr', 'domain', 'vendor', 'model', 'ifAdminStatus', 'ifOperStatus']:
                    value = row_data.get(key, 'N/A')
                    if value and value.strip() and value != '-':
                        print(f"   {key:13s}: {value}")
                    else:
                        print(f"   {key:13s}: None")
            
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False
    
    print("=" * 80)
    
    # Ask for confirmation
    response = input("🤔 Proceed with import? This will replace existing data. (y/N): ")
    if response.lower() != 'y':
        print("❌ Import cancelled")
        return False
    
    # Ask for limit
    if limit is None:
        limit_input = input("📊 Import limit (press Enter for all data, or number): ")
        if limit_input.strip():
            try:
                limit = int(limit_input)
                print(f"📝 Will import first {limit:,} records")
            except ValueError:
                print("📝 Invalid number, will import all data")
        else:
            print("📝 Will import all valid data")
    
    print("\n" + "=" * 80)
    
    # Clear existing data
    print("🗑️ Clearing existing data...")
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM ip_inventory")
        connection.commit()
        cursor.close()
        print("✅ Existing data cleared")
    except Error as e:
        print(f"❌ Error clearing data: {e}")
        return False
    
    # Import data
    print(f"📂 Reading CSV file: {csv_file}")
    print("📊 Starting data import...")
    print("=" * 80)
    
    inserted_count = 0
    skipped_count = 0
    processed_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                processed_count += 1
                
                # Get IP address
                ip_str = row.get('ifIP', '').strip() if row.get('ifIP') else ''
                if not ip_str or ip_str == '-' or ip_str == 'None':
                    skipped_count += 1
                    continue
                
                # Validate IP address
                try:
                    ipaddress.IPv4Address(ip_str)
                except ipaddress.AddressValueError:
                    skipped_count += 1
                    continue
                
                # Calculate subnet
                subnet = calculate_subnet(ip_str)
                if not subnet:
                    skipped_count += 1
                    continue
                
                # Extract data fields with safe handling
                hostname = (row.get('host_name', '') or '').strip()
                service_domain = (row.get('domain', '') or '').strip()
                interface_name = (row.get('ifName', '') or '').strip()
                interface_desc = (row.get('ifDescr', '') or '').strip()
                interface_type = (row.get('ifType', '') or '').strip()
                vendor = (row.get('vendor', '') or '').strip()
                device_model = (row.get('model', '') or '').strip()
                admin_status = (row.get('ifAdminStatus', '') or '').strip()
                oper_status = (row.get('ifOperStatus', '') or '').strip()
                
                # Try to extract VRF information (placeholder for now)
                vrf_vpn = extract_vrf_from_description(interface_desc, interface_name)
                
                # Create description
                desc_parts = []
                if interface_desc and interface_desc != interface_name:
                    desc_parts.append(f"Interface: {interface_desc}")
                if interface_type:
                    desc_parts.append(f"Type: {interface_type}")
                if vendor:
                    desc_parts.append(f"Vendor: {vendor}")
                if device_model:
                    desc_parts.append(f"Model: {device_model}")
                
                description = " | ".join(desc_parts) if desc_parts else None
                
                # Insert into database
                try:
                    cursor = connection.cursor()
                    
                    query = """
                    INSERT INTO ip_inventory 
                    (ip_address, subnet, status, vrf_vpn, hostname, description, service_domain,
                     interface_name, interface_desc, interface_type, vendor, device_model, 
                     admin_status, oper_status) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    values = (ip_str, subnet, 'allocated', vrf_vpn, hostname, description,
                             service_domain, interface_name, interface_desc, interface_type,
                             vendor, device_model, admin_status, oper_status)
                    
                    cursor.execute(query, values)
                    connection.commit()
                    cursor.close()
                    inserted_count += 1
                    
                except Error as e:
                    if "Duplicate entry" not in str(e):
                        print(f"❌ Error inserting IP entry: {e}")
                    skipped_count += 1
                
                # Progress indicator
                if processed_count % 1000 == 0:
                    print(f"📈 Processed {processed_count:,} records, Inserted: {inserted_count:,}, Skipped: {skipped_count:,}")
                
                # Check limit
                if limit and processed_count >= limit:
                    break
    
    except Exception as e:
        print(f"❌ Error during import: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("✅ Database connection closed")
    
    print("=" * 80)
    print("✅ Import completed!")
    print("📊 Summary:")
    print(f"   - Total processed: {processed_count:,}")
    print(f"   - Successfully imported: {inserted_count:,}")
    print(f"   - Skipped: {skipped_count:,}")
    print(f"   - Success rate: {(inserted_count/processed_count*100) if processed_count > 0 else 0:.1f}%")
    
    return True

if __name__ == "__main__":
    import_csv_data()
