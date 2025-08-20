"""
Import CSV data to IPAM database
Parse network inventory CSV and populate ip_inventory table
"""

import mysql.connector
from mysql.connector import Error
import csv
import ipaddress
import re
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '9371',
    'database': 'ipam_db'
}

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return None

def extract_vrf_from_domain(domain):
    """Extract VRF/VPN information from domain field"""
    if not domain:
        return 'default'
    
    # Common VRF patterns
    vrf_mapping = {
        'CGNAT': 'cgnat',
        'MGMT': 'management', 
        'mgmt': 'management',
        'PROD': 'production',
        'prod': 'production',
        'DEV': 'development',
        'dev': 'development',
        'TEST': 'testing',
        'test': 'testing',
        'GUEST': 'guest',
        'guest': 'guest',
        'DMZ': 'dmz',
        'CORE': 'core',
        'ACCESS': 'access'
    }
    
    domain_upper = domain.upper()
    for key, vrf in vrf_mapping.items():
        if key in domain_upper:
            return vrf
    
    return domain.lower()

def calculate_subnet_from_ip(ip_str):
    """Calculate subnet based on IP address (assume /24 for most cases)"""
    try:
        ip_obj = ipaddress.IPv4Address(ip_str)
        
        # Common subnet patterns
        if ip_str.startswith('127.'):
            return '127.0.0.0/8'  # Loopback
        elif ip_str.startswith('10.'):
            return f"{'.'.join(ip_str.split('.')[0:3])}.0/24"  # Private Class A
        elif ip_str.startswith('192.168.'):
            return f"{'.'.join(ip_str.split('.')[0:3])}.0/24"  # Private Class C
        elif ip_str.startswith('172.'):
            # Private Class B (172.16.0.0 - 172.31.255.255)
            return f"{'.'.join(ip_str.split('.')[0:3])}.0/24"
        else:
            # Public IP - assume /24
            return f"{'.'.join(ip_str.split('.')[0:3])}.0/24"
    except:
        return None

def is_valid_ip(ip_str):
    """Check if string is valid IP address"""
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except:
        return False

def import_csv_data(csv_file_path, limit=None):
    """Import data from CSV file to database"""
    try:
        connection = get_db_connection()
        if not connection:
            print("❌ Cannot connect to database")
            return
        
        cursor = connection.cursor()
        
        # Clear existing data
        print("🗑️ Clearing existing data...")
        cursor.execute("DELETE FROM ip_inventory")
        connection.commit()
        
        # Read CSV file
        print(f"📂 Reading CSV file: {csv_file_path}")
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            inserted_count = 0
            skipped_count = 0
            processed_count = 0
            
            print(f"📊 Starting data import...")
            print("=" * 80)
            
            for row in csv_reader:
                processed_count += 1
                
                # Apply limit if specified
                if limit and processed_count > limit:
                    break
                
                # Progress indicator
                if processed_count % 1000 == 0:
                    print(f"📈 Processed {processed_count:,} records, Inserted: {inserted_count:,}, Skipped: {skipped_count:,}")
                
                # Extract data from CSV row
                ip_address = (row.get('ifIP') or '').strip()
                host_name = (row.get('host_name') or '').strip()
                if_name = (row.get('ifName') or '').strip()
                if_descr = (row.get('ifDescr') or '').strip()
                domain = (row.get('domain') or '').strip()
                vendor = (row.get('vendor') or '').strip()
                model = (row.get('model') or '').strip()
                admin_status = (row.get('ifAdminStatus') or '').strip()
                oper_status = (row.get('ifOperStatus') or '').strip()
                
                # Skip if no IP address or invalid IP
                if not ip_address or ip_address == '-' or not is_valid_ip(ip_address):
                    skipped_count += 1
                    continue
                
                # Skip loopback IPs
                if ip_address.startswith('127.'):
                    skipped_count += 1
                    continue
                
                # Calculate subnet
                subnet = calculate_subnet_from_ip(ip_address)
                if not subnet:
                    skipped_count += 1
                    continue
                
                # Extract VRF from domain
                vrf_vpn = extract_vrf_from_domain(domain)
                
                # Determine status based on admin and operational status
                if admin_status == 'Up' and oper_status == 'Up':
                    status = 'used'
                elif admin_status == 'Up' and oper_status == 'Down':
                    status = 'reserved'
                else:
                    status = 'available'
                
                # Create description
                description_parts = []
                if if_name:
                    description_parts.append(f"Interface: {if_name}")
                if if_descr and if_descr != if_name:
                    description_parts.append(f"Desc: {if_descr}")
                if vendor:
                    description_parts.append(f"Vendor: {vendor}")
                if model:
                    description_parts.append(f"Model: {model}")
                
                description = " | ".join(description_parts) if description_parts else f"Imported from CSV - {host_name}"
                
                # Create hostname
                hostname = host_name if host_name else f"host-{ip_address.replace('.', '-')}"
                
                try:
                    # Insert into database
                    cursor.execute("""
                        INSERT INTO ip_inventory 
                        (ip_address, subnet, status, vrf_vpn, hostname, description)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        status = VALUES(status),
                        vrf_vpn = VALUES(vrf_vpn),
                        hostname = VALUES(hostname),
                        description = VALUES(description),
                        updated_at = CURRENT_TIMESTAMP
                    """, (ip_address, subnet, status, vrf_vpn, hostname, description))
                    
                    inserted_count += 1
                    
                except Error as e:
                    if "Duplicate entry" not in str(e):
                        print(f"⚠️ Error inserting {ip_address}: {e}")
                    skipped_count += 1
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("=" * 80)
        print(f"✅ Import completed!")
        print(f"📊 Summary:")
        print(f"   - Total processed: {processed_count:,}")
        print(f"   - Successfully imported: {inserted_count:,}")
        print(f"   - Skipped: {skipped_count:,}")
        print(f"   - Success rate: {(inserted_count/processed_count*100):.1f}%")
        
        return inserted_count
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
        return 0

def analyze_csv_structure(csv_file_path, sample_rows=10):
    """Analyze CSV structure and show sample data"""
    try:
        print(f"🔍 Analyzing CSV structure: {csv_file_path}")
        print("=" * 80)
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Show headers
            headers = csv_reader.fieldnames
            print(f"📋 Headers ({len(headers)} columns):")
            for i, header in enumerate(headers, 1):
                print(f"   {i:2d}. {header}")
            
            print("\n📊 Sample data:")
            print("-" * 80)
            
            # Show sample rows
            for i, row in enumerate(csv_reader):
                if i >= sample_rows:
                    break
                    
                print(f"\nRow {i+1}:")
                # Show only relevant fields
                relevant_fields = ['ifIP', 'host_name', 'ifName', 'ifDescr', 'domain', 'vendor', 'model', 'ifAdminStatus', 'ifOperStatus']
                for field in relevant_fields:
                    if field in row:
                        value = row[field][:50] if len(str(row[field])) > 50 else row[field]
                        print(f"   {field:15}: {value}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error analyzing CSV: {e}")

if __name__ == '__main__':
    csv_file = 'datalake.Inventory.port.csv'
    
    print("🚀 IPAM CSV Import Tool")
    print("=" * 80)
    
    # Analyze CSV structure first
    analyze_csv_structure(csv_file, sample_rows=5)
    
    # Ask for confirmation
    print("\n" + "=" * 80)
    confirm = input("🤔 Proceed with import? This will replace existing data. (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        # Ask for limit
        limit_input = input("📊 Import limit (press Enter for all data, or number): ").strip()
        limit = None
        if limit_input.isdigit():
            limit = int(limit_input)
            print(f"📝 Will import maximum {limit:,} records")
        else:
            print("📝 Will import all valid data")
        
        # Import data
        print("\n" + "=" * 80)
        import_csv_data(csv_file, limit=limit)
    else:
        print("❌ Import cancelled")
