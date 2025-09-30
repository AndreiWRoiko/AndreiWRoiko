# Equipment Inventory System

## Overview

This is a Flask-based equipment inventory management system designed for tracking IT equipment across multiple locations and organizations. The system provides comprehensive equipment tracking with features including equipment registration, status monitoring, location management, and detailed reporting. It's built with a focus on Brazilian business requirements, supporting UF (state) tracking, CNPJ management, and Portuguese language interfaces.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework Architecture
- **Flask Application**: Core web framework with modular structure
- **SQLAlchemy ORM**: Database abstraction layer with declarative base model
- **Flask-WTF Forms**: Form handling and validation with CSRF protection
- **Template Engine**: Jinja2 templating with Bootstrap-based responsive UI

### Database Design
- **Single Table Model**: Equipment table storing all inventory data
- **PostgreSQL Database**: Production-ready database with full feature support
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability
- **Automatic Schema Creation**: Database tables created on application startup
- **Data Import/Export**: Excel import functionality with template download and comprehensive validation

### Frontend Architecture
- **Bootstrap 5**: Dark theme responsive UI framework
- **Plotly.js**: Interactive data visualization for dashboard charts
- **Font Awesome**: Icon library for consistent visual elements
- **Progressive Enhancement**: JavaScript features that gracefully degrade

### Data Management
- **Form Validation**: Server-side validation with WTForms
- **Export Capabilities**: Excel and PDF export functionality
- **Import Functionality**: Excel file import with duplicate checking and data validation
- **Search and Filtering**: Multi-criteria equipment search system
- **Pagination**: Efficient data display for large equipment lists
- **Template Download**: Excel template generation for consistent data import format

### Application Structure
- **Modular Design**: Separated routes, models, forms, and utilities
- **Template Inheritance**: Base template system for consistent UI
- **Static Asset Management**: Organized CSS and JavaScript files
- **Environment Configuration**: Flexible configuration via environment variables

### Security Features
- **CSRF Protection**: Built-in form security
- **Session Management**: Secure session handling with configurable secret keys
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: CSS framework from CDN with agent-specific dark theme
- **Font Awesome 6.4.0**: Icon library from cdnjs.cloudflare.com
- **Plotly.js**: Data visualization library from cdn.plot.ly

### Python Packages
- **Flask**: Web framework and core functionality
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-WTF**: Form handling and validation
- **WTForms**: Form field types and validators
- **Pandas**: Data manipulation for export features
- **ReportLab**: PDF generation capabilities
- **Plotly**: Server-side chart generation
- **Werkzeug**: WSGI utilities and proxy middleware

### Database Support
- **PostgreSQL**: Primary database with full production capabilities
- **SQLite**: Fallback option for development
- **Connection Management**: Automatic pool management and health checks
- **Sample Data**: Pre-populated with example equipment records for testing

### Deployment Infrastructure
- **Environment Variables**: Configuration via SESSION_SECRET and DATABASE_URL
- **WSGI Compatibility**: Standard WSGI application structure
- **Production Server**: Gunicorn WSGI server with autoscaling deployment configuration
- **Development Server**: Built-in Flask development server with debugging
- **Static File Serving**: Flask static file handling for CSS and JavaScript assets
- **Replit Integration**: Fully configured for Replit environment with PostgreSQL database

## Recent Changes (September 30, 2025)

### GitHub Import Setup - COMPLETED (September 30, 2025)
- ✅ **Fresh GitHub Clone**: Successfully imported and configured for Replit environment
- ✅ **Dependencies Installed**: All Python packages installed via UV package manager
  - Used `uv sync` to install 44 packages from pyproject.toml and uv.lock
  - Virtual environment created at `.pythonlibs/`
- ✅ **PostgreSQL Database**: Created and configured with environment variables
  - Database tables automatically created on first run
  - Admin user created: username `admin`, password `Admin123!`, email `admin@inventory.local`
- ✅ **Workflow Configuration**: Flask app running on port 5000 with webview output
  - Command: `.pythonlibs/bin/python main.py`
  - Server bound to 0.0.0.0:5000 for Replit proxy compatibility
  - Application tested and verified working correctly
- ✅ **Deployment Configuration**: Configured for autoscale deployment with Gunicorn
  - Command: `.pythonlibs/bin/gunicorn --bind 0.0.0.0:5000 --reuse-port --workers 2 wsgi:app`
  - Production-ready WSGI server configuration
- ✅ **.gitignore Updated**: Enhanced with comprehensive Python ignore patterns
  - Virtual environment (.pythonlibs/)
  - Python build artifacts
  - Test coverage reports
  - Upload directories

## Recent Changes (Previous - September 30, 2025)

### Export Functionality Security Enhancement - COMPLETED (September 30, 2025)
- ✅ **Secure Export Implementation**: Implemented safe Excel and PDF export functionality
  - Replaced temporary file handling with in-memory BytesIO buffers
  - Eliminated security risk of persistent temporary files containing sensitive data
  - Export methods now use memory-only processing (no disk writes)
  - Proper buffer management with seek(0) before returning to send_file
- ✅ **Export Features**:
  - Excel export with comprehensive equipment data (pandas + openpyxl)
  - PDF export with formatted tables and report headers (reportlab)
  - Filter support: UF, status, tipo_equipamento, centro_custo_id
  - Search functionality across patrimônio, responsável, modelo, marca, fornecedor
  - Permission-gated access (requires 'view' permission)
  - Automatic timestamped filenames for downloads
- ✅ **Security Improvements**:
  - No temporary files left on disk (prevents data leaks)
  - No file descriptor leaks (proper memory buffer management)
  - Parameterized SQLAlchemy queries (prevents SQL injection)
  - Authorized access only (permission checks in routes)

### Fresh GitHub Clone Setup - COMPLETED (September 30, 2025)
- ✅ **Fresh Clone**: Successfully imported and configured fresh GitHub clone for Replit environment
- ✅ **Dependencies**: All Python packages installed via UV package manager (uv sync)
  - Created virtual environment at `.pythonlibs/` with 44 packages
  - All dependencies from pyproject.toml and uv.lock installed successfully
- ✅ **Database Setup**: PostgreSQL database configured and tables initialized successfully
  - Database URL: `postgresql://postgres:password@helium/heliumdb`
  - All tables created automatically on first run
- ✅ **Admin User**: Created default admin user
  - **Username:** admin
  - **Password:** Admin123!
  - **Email:** admin@inventory.local
  - **Role:** ADM (Administrator)
  - **Status:** Approved and ready for use
- ✅ **Workflow Configuration**: Flask app running on port 5000 with webview output
  - Uses `.pythonlibs/bin/python main.py` to run from virtual environment
  - Server bound to 0.0.0.0:5000 for Replit proxy support
  - Application tested and verified working correctly
- ✅ **Deployment Configuration**: Configured for autoscale deployment
  - Uses Gunicorn production server with 2 workers
  - Command: `.pythonlibs/bin/gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 wsgi:app`
- ✅ **Type Hints Fixed**: Updated type annotations in db.py for Python 3.11 compatibility

### Previous Development History (September 29, 2025)
- ✅ **Complete System Restructuring**: Reorganized entire codebase into professional modular architecture
  - `inventory_app/` - Main application package with application factory pattern
  - `inventory_app/models/` - Database models (User, Equipment, CentroCusto, Kanban)  
  - `inventory_app/services/` - Business logic layer (AuthService, EquipmentService, UserService)
  - `inventory_app/blueprints/` - Route organization (auth, main, inventory, admin)
  - `inventory_app/forms/` - WTForms for validation
  - `inventory_app/config.py` - Environment-based configuration management
  - `inventory_app/extensions.py` - Flask extensions (SQLAlchemy, Flask-Login, Flask-Migrate)
- ✅ **Database Optimizations**: Added indexes, proper relationships, connection pooling for PostgreSQL
- ✅ **Security Improvements**: Enhanced configuration management, proper secret handling
- ✅ **Development Tools**: Added Flask-Migrate for database migrations, management CLI commands

### Configuration Details
- **Server**: Flask development server for development, Gunicorn for production deployment
- **Database**: PostgreSQL with connection pooling and health checks
- **Host Configuration**: Bound to 0.0.0.0:5000 to allow proxy access through Replit
- **Environment Secrets**: SESSION_SECRET and DATABASE_URL properly configured
- **Workflow Status**: Running successfully on port 5000 with webview interface

### Environment Variables for Production
For production deployment, configure these environment variables:
- **SESSION_SECRET**: Secure session encryption key (auto-generated in development)
- **DATABASE_URL**: PostgreSQL connection string (defaults to SQLite in development)

### First-Time Setup
1. **Admin user has been created and configured:**
   - **Username:** admin
   - **Password:** Admin123
   - **Role:** ADM (Administrator)
   - **Status:** Approved and ready for use

2. **Application Features Available:**
   - User authentication and role-based access control
   - Equipment inventory management with full CRUD operations
   - PostgreSQL database with proper data persistence
   - Excel import/export functionality
   - Professional responsive UI with Bootstrap
   - Data visualization and reporting features

3. **System Architecture Successfully Implemented:**
   - Modular package structure with separation of concerns
   - Application factory pattern for Flask initialization
   - Service layer for business logic organization
   - Blueprint-based routing system for code organization
   - PostgreSQL-only database configuration (no SQLite fallback)
   - Flask-Migrate for database schema management

### Ready for Production
The application has been completely restructured and is fully ready for production deployment using Replit's publishing system. The system provides a professional, scalable equipment inventory management solution.