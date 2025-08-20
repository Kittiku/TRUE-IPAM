import mysql.connector
from mysql.connector import Error
import ipaddress

class MySQLManager:
    def __init__(self, host='localhost', database='ipam_system', user='root', password=''):
        """Initialize MySQL connection"""
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            
            if self.connection.is_connected():
                print("✅ Successfully connected to MySQL database")
                return True
                
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            
            # Try to create database if it doesn't exist
            try:
                connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password
                )
                cursor = connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                connection.commit()
                cursor.close()
                connection.close()
                
                # Try connecting again
                self.connection = mysql.connector.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci'
                )
                print("✅ Database created and connected successfully")
                return True
                
            except Error as e2:
                print(f"❌ Error creating database: {e2}")
                return False
        
        return False

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Create enhanced ip_inventory table with service and interface data
            create_table_query = """
            CREATE TABLE IF NOT EXISTS ip_inventory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ip_address VARCHAR(45) NOT NULL UNIQUE,
                subnet VARCHAR(18) NOT NULL,
                status ENUM('available', 'allocated', 'reserved') DEFAULT 'allocated',
                vrf_vpn VARCHAR(100),
                hostname VARCHAR(255),
                description TEXT,
                service_domain VARCHAR(100),
                interface_name VARCHAR(100),
                interface_desc VARCHAR(255),
                interface_type VARCHAR(50),
                vendor VARCHAR(100),
                device_model VARCHAR(100),
                admin_status VARCHAR(20),
                oper_status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_ip (ip_address),
                INDEX idx_subnet (subnet),
                INDEX idx_vrf_vpn (vrf_vpn),
                INDEX idx_service (service_domain),
                INDEX idx_hostname (hostname),
                INDEX idx_interface (interface_name)
            )
            """
            
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            print("✅ Database tables created successfully")
            
        except Error as e:
            print(f"❌ Error creating tables: {e}")
            return False
        
        return True

    def insert_ip_entry(self, ip_address, subnet, status='allocated', vrf_vpn=None, 
                       hostname=None, description=None, service_domain=None,
                       interface_name=None, interface_desc=None, interface_type=None,
                       vendor=None, device_model=None, admin_status=None, oper_status=None):
        """Insert a new IP entry into the database"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO ip_inventory 
            (ip_address, subnet, status, vrf_vpn, hostname, description, service_domain,
             interface_name, interface_desc, interface_type, vendor, device_model, 
             admin_status, oper_status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (ip_address, subnet, status, vrf_vpn, hostname, description,
                     service_domain, interface_name, interface_desc, interface_type,
                     vendor, device_model, admin_status, oper_status)
            
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            if "Duplicate entry" not in str(e):
                print(f"❌ Error inserting IP entry: {e}")
            return False

    def get_all_ips(self):
        """Retrieve all IP entries from database"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM ip_inventory ORDER BY INET_ATON(ip_address)")
            result = cursor.fetchall()
            cursor.close()
            return result
            
        except Error as e:
            print(f"❌ Error retrieving IPs: {e}")
            return []

    def get_subnets_by_cidr(self, cidr_suffix):
        """Get subnet statistics by CIDR"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                subnet,
                COUNT(*) as total_ips,
                COUNT(CASE WHEN status = 'allocated' THEN 1 END) as allocated_ips,
                COUNT(CASE WHEN status = 'available' THEN 1 END) as available_ips,
                COUNT(CASE WHEN status = 'reserved' THEN 1 END) as reserved_ips,
                GROUP_CONCAT(DISTINCT vrf_vpn) as vrf_list,
                GROUP_CONCAT(DISTINCT service_domain) as service_list,
                GROUP_CONCAT(DISTINCT vendor) as vendor_list
            FROM ip_inventory 
            WHERE subnet LIKE %s
            GROUP BY subnet
            ORDER BY INET_ATON(SUBSTRING_INDEX(subnet, '/', 1))
            """
            
            cursor.execute(query, (f'%/{cidr_suffix}',))
            result = cursor.fetchall()
            cursor.close()
            return result
            
        except Error as e:
            print(f"❌ Error getting subnets: {e}")
            return []

    def get_vrf_stats(self):
        """Get VRF/VPN statistics"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                COALESCE(vrf_vpn, 'Unknown') as vrf_name,
                COUNT(*) as ip_count,
                COUNT(DISTINCT subnet) as subnet_count,
                COUNT(DISTINCT hostname) as device_count
            FROM ip_inventory 
            GROUP BY vrf_vpn
            ORDER BY ip_count DESC
            """
            
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
            
        except Error as e:
            print(f"❌ Error getting VRF stats: {e}")
            return []

    def get_service_stats(self):
        """Get Service Domain statistics"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                COALESCE(service_domain, 'Unknown') as service_name,
                COUNT(*) as ip_count,
                COUNT(DISTINCT subnet) as subnet_count,
                COUNT(DISTINCT hostname) as device_count,
                COUNT(DISTINCT vendor) as vendor_count
            FROM ip_inventory 
            GROUP BY service_domain
            ORDER BY ip_count DESC
            """
            
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
            
        except Error as e:
            print(f"❌ Error getting service stats: {e}")
            return []

    def clear_all_data(self):
        """Clear all data from ip_inventory table"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM ip_inventory")
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            print(f"❌ Error clearing data: {e}")
            return False

    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ MySQL connection closed")

    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close_connection()
