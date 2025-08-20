#!/usr/bin/env python3
"""
Simple IPAM CSV Import with Service Information
Uses existing database structure but adds service data to description field
"""

import csv
import ipaddress
import re

def extract_service_info(domain, vendor, model, interface_type):
    """Extract service information from CSV data"""
    service_info = []
    
    if domain and domain.strip():
        service_info.append(f"Service: {domain.strip()}")
    
    if vendor and vendor.strip():
        service_info.append(f"Vendor: {vendor.strip()}")
    
    if model and model.strip():
        service_info.append(f"Model: {model.strip()}")
    
    if interface_type and interface_type.strip():
        service_info.append(f"Type: {interface_type.strip()}")
    
    return " | ".join(service_info) if service_info else None

def try_extract_vrf(description, hostname):
    """Try to extract VRF from description or hostname"""
    if not description and not hostname:
        return None
    
    text = f"{description or ''} {hostname or ''}".upper()
    
    # Look for VRF patterns
    vrf_patterns = [
        r'VRF[_-]?(\w+)',
        r'VPN[_-]?(\w+)',
        r'MPLS[_-]?(\w+)',
        r'RD[_-]?(\d+:\d+)'
    ]
    
    for pattern in vrf_patterns:
        match = re.search(pattern, text)
        if match:
            return f"VRF_{match.group(1)}"
    
    return None

def calculate_subnet(ip_str, default_prefix=24):
    """Calculate subnet from IP address"""
    try:
        ip = ipaddress.IPv4Address(ip_str)
        
        # Determine subnet based on IP class
        if ip.is_private:
            if str(ip).startswith('10.'):
                prefix = 16
            elif str(ip).startswith('192.168.'):
                prefix = 24
            elif str(ip).startswith('172.'):
                prefix = 20
            else:
                prefix = default_prefix
        else:
            prefix = default_prefix
            
        network = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
        return str(network)
        
    except (ipaddress.AddressValueError, ValueError):
        return None

def import_csv_with_service_data(csv_file='datalake.Inventory.port.csv', limit=None):
    """Import CSV data with service information"""
    
    print("🚀 IPAM CSV Import with Service Data")
    print("=" * 60)
    
    # Database connection
    import mysql.connector
    from mysql.connector import Error
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ipam_db',
            user='root',
            password='9371',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            print("✅ Connected to database")
        else:
            print("❌ Failed to connect to database")
            return False
            
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    # Analyze CSV
    print(f"🔍 Analyzing CSV: {csv_file}")
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            
            print(f"📋 Found {len(headers)} columns")
            
            # Show sample service data
            print("\n📊 Sample service data:")
            for i in range(3):
                try:
                    row = next(reader)
                    row_data = dict(zip(headers, row))
                    
                    ip = row_data.get('ifIP', 'N/A')
                    domain = row_data.get('domain', 'N/A')
                    vendor = row_data.get('vendor', 'N/A')
                    hostname = row_data.get('host_name', 'N/A')
                    
                    print(f"  Row {i+1}: IP={ip}, Service={domain}, Vendor={vendor}, Host={hostname}")
                    
                except StopIteration:
                    break
                    
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False
    
    # Ask for confirmation
    response = input(f"\n🤔 Proceed with import? (y/N): ")
    if response.lower() != 'y':
        print("❌ Import cancelled")
        return False
    
    # Ask for limit
    if limit is None:
        limit_input = input("📊 Import limit (Enter for all, or number): ")
        if limit_input.strip():
            try:
                limit = int(limit_input)
                print(f"📝 Will import first {limit:,} valid records")
            except ValueError:
                print("📝 Will import all valid data")
        else:
            print("📝 Will import all valid data")
    
    print("\n" + "=" * 60)
    
    # Clear existing data
    print("🗑️ Clearing existing data...")
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM ip_inventory")
        connection.commit()
        cursor.close()
        print("✅ Data cleared")
    except Error as e:
        print(f"❌ Error clearing data: {e}")
        return False
    
    # Import data
    print("📂 Starting import...")
    print("=" * 60)
    
    inserted_count = 0
    skipped_count = 0
    processed_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                processed_count += 1
                
                # Get IP address
                ip_str = (row.get('ifIP', '') or '').strip()
                if not ip_str or ip_str == '-' or ip_str == 'None':
                    skipped_count += 1
                    continue
                
                # Validate IP
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
                
                # Extract data
                hostname = (row.get('host_name', '') or '').strip()
                domain = (row.get('domain', '') or '').strip()
                vendor = (row.get('vendor', '') or '').strip()
                model = (row.get('model', '') or '').strip()
                interface_type = (row.get('ifType', '') or '').strip()
                interface_name = (row.get('ifName', '') or '').strip()
                interface_desc = (row.get('ifDescr', '') or '').strip()
                
                # Create service description
                service_info = extract_service_info(domain, vendor, model, interface_type)
                
                # Try to extract VRF
                vrf_vpn = try_extract_vrf(interface_desc, hostname) or domain
                
                # Combined description
                desc_parts = []
                if service_info:
                    desc_parts.append(service_info)
                if interface_name and interface_name != interface_desc:
                    desc_parts.append(f"Interface: {interface_name}")
                if interface_desc and interface_desc != interface_name:
                    desc_parts.append(f"Description: {interface_desc}")
                
                description = " | ".join(desc_parts) if desc_parts else None
                
                # Insert into database using existing structure
                try:
                    cursor = connection.cursor()
                    
                    query = """
                    INSERT INTO ip_inventory 
                    (ip_address, subnet, status, vrf_vpn, hostname, description) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    
                    values = (ip_str, subnet, 'used', vrf_vpn, hostname, description)
                    
                    cursor.execute(query, values)
                    connection.commit()
                    cursor.close()
                    inserted_count += 1
                    
                except Error as e:
                    if "Duplicate entry" not in str(e):
                        print(f"❌ Error inserting {ip_str}: {e}")
                    skipped_count += 1
                
                # Progress
                if processed_count % 1000 == 0:
                    print(f"📈 Processed: {processed_count:,}, Inserted: {inserted_count:,}, Skipped: {skipped_count:,}")
                
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
    
    print("=" * 60)
    print("✅ Import completed!")
    print("📊 Summary:")
    print(f"   - Total processed: {processed_count:,}")
    print(f"   - Successfully imported: {inserted_count:,}")
    print(f"   - Skipped: {skipped_count:,}")
    print(f"   - Success rate: {(inserted_count/processed_count*100) if processed_count > 0 else 0:.1f}%")
    
    # Show service breakdown
    if inserted_count > 0:
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='ipam_db',
                user='root',
                password='9371'
            )
            
            cursor = connection.cursor(dictionary=True)
            
            print("\n📊 Service Breakdown:")
            cursor.execute("""
                SELECT 
                    COALESCE(vrf_vpn, 'Unknown') as service,
                    COUNT(*) as ip_count,
                    COUNT(DISTINCT subnet) as subnet_count
                FROM ip_inventory 
                GROUP BY vrf_vpn 
                ORDER BY ip_count DESC 
                LIMIT 10
            """)
            
            services = cursor.fetchall()
            for service in services:
                print(f"   - {service['service']}: {service['ip_count']} IPs, {service['subnet_count']} subnets")
            
            cursor.close()
            connection.close()
            
        except Error as e:
            print(f"⚠️ Could not show service breakdown: {e}")
    
    return True

if __name__ == "__main__":
    import_csv_with_service_data()
