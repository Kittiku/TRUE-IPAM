# TRUE-IPAM: IP Address Management System

A comprehensive IP Address Management system built with Flask and MySQL for enterprise network administration.

## 🚀 Production-Ready Features

- **Complete IP Management**: Full CRUD operations with individual IP editing
- **Bulk Operations**: Subnet-wide status changes and service assignments  
- **Advanced Filtering**: CIDR, IP range, and service domain filtering
- **Real-time Dashboard**: Live statistics and utilization monitoring
- **Service Domain Tracking**: VRF/VPN management and monitoring
- **Click-to-Edit Interface**: Intuitive IP address modification
- **Toast Notifications**: User-friendly feedback system

## 📁 Clean Project Structure

```
TRUE-IPAM/
├── main_server.py              # Flask application (Production)
├── mysql_manager.py            # Database connection manager
├── import_csv_data.py          # CSV data import utility
├── requirements.txt            # Python dependencies
├── start_ipam.bat             # Windows startup script
├── datalake.Inventory.port.csv # Sample data
│
├── templates/                  # Active templates only
│   ├── ip_management_clean.html # Main IPAM interface
│   └── subnet_monitor.html     # Subnet monitoring
│
├── static/js/                  # Frontend assets
│   └── app.js                 # JavaScript functionality
│
└── old/                       # Archived legacy files
    ├── servers/               # Previous server versions
    ├── templates/             # Old UI templates
    ├── scripts/               # Utility scripts
    └── docs/                  # Legacy documentation
```

## ⚡ Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/Kittiku/TRUE-IPAM.git
cd TRUE-IPAM
```

2. **Setup Python environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. **Configure MySQL**
- Update connection settings in `mysql_manager.py`
- Database: `ipam_db` (auto-created)

4. **Launch the system**
```bash
python main_server.py
# OR
start_ipam.bat
```

5. **Access the interface**
- Main IPAM: http://127.0.0.1:5005/ip-management
- Subnet Monitor: http://127.0.0.1:5005/subnet-monitor

## 🎯 Key Capabilities

### Individual IP Management
- **Click any IP address** to edit details (IP, status, hostname, description)
- **Quick status buttons** for one-click status changes
- **Real-time validation** and error handling

### Bulk Subnet Operations
- **Change Status**: Update all IPs in subnet to specific status
- **Assign Service**: Assign service domain to entire subnet
- **Reserve Range**: Reserve specific IP ranges within subnet
- **Release Range**: Release specific IP ranges

### Advanced Filtering
- **CIDR Filtering**: Filter subnets by prefix length
- **IP Range Filtering**: Show subnets within specific IP ranges
- **Service Domain Filtering**: Filter by VRF/service assignment
- **Status Filtering**: Filter by utilization levels

## 🗃️ Database Schema

### ip_inventory
```sql
ip_address (VARCHAR, PRIMARY KEY)
status (ENUM: used, available, reserved)
vrf_vpn (VARCHAR) - Service domain assignment  
hostname (VARCHAR) - Device hostname
description (TEXT) - Additional notes
subnet (VARCHAR) - Associated subnet
created_at, updated_at (TIMESTAMP)
```

### subnets
```sql
id (INT, AUTO_INCREMENT PRIMARY KEY)
subnet (VARCHAR) - CIDR notation
description (TEXT) - Subnet description
service_domain (VARCHAR) - Assigned service
status (ENUM: active, inactive)
created_at, updated_at (TIMESTAMP)
```

## 🔧 API Endpoints

### Core Operations
- `GET /api/subnet-monitor` - Subnet statistics and monitoring
- `GET /api/subnet-detail/<subnet>` - Detailed subnet information
- `GET /api/ip-details?ip=<ip>` - Individual IP details

### IP Management
- `PUT /api/edit-ip/<ip>` - Full IP edit (address, status, details)
- `PUT /api/quick-edit-ip/<ip>` - Quick status change
- `POST /api/bulk-edit-subnet` - Bulk subnet operations

### Data Import
- `POST /api/add-ip` - Add new IP address
- Support for CSV import via `import_csv_data.py`

## 📊 Sample Data

Includes real-world sample data with:
- **46,400+ IP addresses** across multiple service domains
- **Realistic distribution**: 48.7% used, 41.1% available, 10.2% reserved
- **Service domains**: IPRAN-D, RN/AGN, IPCORE-BB, IPCORE-MB, etc.
- **Multiple subnet sizes**: /16, /20, /24, /28 networks

## 🔄 Migration from Legacy

All previous development files are organized in the `old/` directory:
- Server versions, templates, scripts, and documentation
- Preserved for reference and potential feature extraction
- See `old/README_ARCHIVE.md` for detailed inventory

## 🚀 Production Deployment

For production environments:
1. Use WSGI server (Gunicorn/uWSGI)
2. Configure MySQL with connection pooling
3. Set up reverse proxy (Nginx/Apache)
4. Enable SSL/HTTPS
5. Configure logging and monitoring

## 📈 System Statistics

Current data includes:
- **Service Domains**: 10 active domains
- **Total IPs**: 46,400+ addresses
- **Subnet Types**: /16 to /30 networks
- **Utilization**: Realistic enterprise-level distribution

## 🛠️ Development Notes

- **Framework**: Flask with MySQL backend
- **Frontend**: Modern HTML5/CSS3 with Tailwind CSS
- **JavaScript**: Vanilla JS with async/await patterns
- **Database**: MySQL with optimized queries
- **Architecture**: RESTful API design

## 📝 License

Proprietary software for enterprise network management.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

---

**Version**: 2.0 Production  
**Last Updated**: August 2025  
**Status**: Production Ready  
**Repository**: https://github.com/Kittiku/TRUE-IPAM
