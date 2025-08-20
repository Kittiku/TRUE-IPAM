"""
Create sample data for testing subnet monitor
"""

import mysql.connector
from mysql.connector import Error
import ipaddress
import random

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

def create_sample_data():
    """Create sample IP data for testing"""
    try:
        connection = get_db_connection()
        if not connection:
            print("❌ Cannot connect to database")
            return
            
        cursor = connection.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM ip_inventory")
        print("🗑️ Cleared existing data")
        
        # Define sample subnets and their usage
        subnets_data = [
            # /24 subnets
            {"network": "10.11.17.0/24", "used_count": 2, "reserved_count": 0},
            {"network": "10.13.0.0/24", "used_count": 25, "reserved_count": 3},
            {"network": "10.13.1.0/24", "used_count": 18, "reserved_count": 3},
            {"network": "10.13.4.0/24", "used_count": 25, "reserved_count": 3},
            {"network": "10.13.8.0/24", "used_count": 30, "reserved_count": 4},
            {"network": "10.13.9.0/24", "used_count": 2, "reserved_count": 1},
            
            # Different /24 subnets to avoid overlap
            {"network": "10.13.2.0/24", "used_count": 3, "reserved_count": 0},
            {"network": "10.13.5.0/24", "used_count": 15, "reserved_count": 0},
        ]
        
        sample_hostnames = [
            "server01", "workstation01", "printer01", "router01", "switch01",
            "firewall01", "server02", "workstation02", "printer02", "router02",
            "switch02", "firewall02", "server03", "workstation03", "printer03",
            "router03", "switch03", "firewall03", "server04", "workstation04",
            "printer04", "router04", "switch04", "firewall04", "server05"
        ]
        
        sample_descriptions = [
            "Main server", "Employee workstation", "Network printer", "Core router",
            "Access switch", "Security firewall", "Database server", "Development machine",
            "Shared printer", "Edge router", "Distribution switch", "Perimeter firewall",
            "Web server", "Testing workstation", "Color printer", "Backup router",
            "Core switch", "Internal firewall", "Application server", "Admin workstation",
            "Label printer", "Redundant router", "Access switch", "DMZ firewall", "Mail server"
        ]
        
        vrf_vpns = ["default", "management", "production", "development", "guest"]
        
        insert_count = 0
        
        for subnet_info in subnets_data:
            network = ipaddress.IPv4Network(subnet_info["network"])
            used_count = subnet_info["used_count"]
            reserved_count = subnet_info["reserved_count"]
            
            # Get list of all IPs in the subnet (excluding network and broadcast if applicable)
            if network.prefixlen < 31:
                all_ips = list(network.hosts())
            else:
                all_ips = list(network)
            
            # Randomly select IPs to mark as used
            used_ips = random.sample(all_ips, min(used_count, len(all_ips)))
            
            # Select IPs for reserved (from remaining IPs)
            remaining_ips = [ip for ip in all_ips if ip not in used_ips]
            reserved_ips = random.sample(remaining_ips, min(reserved_count, len(remaining_ips)))
            
            # Insert used IPs
            for i, ip in enumerate(used_ips):
                hostname = random.choice(sample_hostnames)
                description = random.choice(sample_descriptions)
                vrf_vpn = random.choice(vrf_vpns)
                
                cursor.execute("""
                    INSERT INTO ip_inventory 
                    (ip_address, subnet, status, vrf_vpn, hostname, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (str(ip), str(network), 'used', vrf_vpn, hostname, description))
                insert_count += 1
            
            # Insert reserved IPs
            for ip in reserved_ips:
                cursor.execute("""
                    INSERT INTO ip_inventory 
                    (ip_address, subnet, status, vrf_vpn, hostname, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (str(ip), str(network), 'reserved', 'management', 'reserved', 'Reserved for future use'))
                insert_count += 1
        
        connection.commit()
        print(f"✅ Created {insert_count} sample IP records")
        print("📊 Sample data includes:")
        for subnet_info in subnets_data:
            print(f"   - {subnet_info['network']}: {subnet_info['used_count']} used, {subnet_info['reserved_count']} reserved")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Error creating sample data: {e}")
    except Exception as e:
        print(f"❌ General error: {e}")

if __name__ == '__main__':
    print("🚀 Creating sample data for IPAM system...")
    create_sample_data()
    print("✅ Sample data creation completed!")
