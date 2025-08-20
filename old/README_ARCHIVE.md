# IPAM Legacy Files Archive

This directory contains archived files from previous development iterations of the IPAM system.

## 📁 Directory Structure

### /servers
Contains previous server implementations:
- `advanced_server.py` - Enhanced server with additional features
- `main_server_clean.py` - Clean version of main server
- `main_server_new.py` - Newer iteration of main server
- `mysql_manager_enhanced.py` - Enhanced database manager

### /templates  
Contains legacy HTML templates:
- `advanced_dashboard.html` - Advanced dashboard interface
- `advanced_ipam.html` - Advanced IPAM features interface
- `ip_management.html` - Original IP management interface
- `ip_management_advanced.html` - Advanced IP management interface
- `main_dashboard.html` - Main dashboard template
- `test_dashboard.html` - Testing dashboard

### /scripts
Contains utility and migration scripts:
- `calculate_real_ips.py` - IP calculation utility
- `check_data.py` - Data validation script
- `check_status.py` - Status checking utility
- `check_subnets.py` - Subnet validation script
- `check_table_structure.py` - Database structure checker
- `check_vrf_data.py` - VRF data validation
- `create_sample_data.py` - Sample data generation
- `fix_ip_status.py` - IP status correction script
- `import_enhanced_data.py` - Enhanced data import
- `import_service_data.py` - Service data import

### /docs
Contains legacy documentation:
- `PROJECT_STRUCTURE.md` - Original project structure documentation
- `SUBNET_MANAGEMENT_ENHANCEMENT.md` - Subnet management enhancement docs
- `SUBNET_MONITOR_README.md` - Subnet monitoring documentation
- `VRF_UPDATE_SUMMARY.md` - VRF update summary

## 🗃 Archive Information

**Archive Date**: August 20, 2025  
**Reason**: Project restructuring and cleanup  
**Status**: Reference only - not for active use

## ⚠️ Important Notes

- These files are kept for reference and historical purposes
- Do NOT use these files in the production system
- The active system uses only the files in the parent directory
- Some scripts may contain useful logic for future development

## 🔍 File Usage History

### Most Recent Active Files (before archiving):
- `main_server_clean.py` - Was the clean version before final merge
- `ip_management_clean.html` - Current production template is derived from this
- `fix_ip_status.py` - Successfully fixed realistic IP status distribution

### Development Scripts:
- Various `check_*.py` scripts were used during development for data validation
- `import_*.py` scripts were used for data migration and testing

### UI Evolution:
- Templates show the evolution from basic to advanced IPAM interface
- Current production UI combines best features from these iterations

## 🚀 Migration Notes

If you need to reference any functionality from these archived files:

1. Review the file content carefully
2. Extract only the specific functionality needed
3. Adapt the code to work with the current system architecture
4. Test thoroughly before implementing

---

**Archived by**: System Cleanup Process  
**Archive Version**: v1.0  
**Contact**: Development Team
