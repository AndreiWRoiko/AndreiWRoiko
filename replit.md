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

## Recent Changes (September 29, 2025)

### Complete System Restructuring - COMPLETED (September 29, 2025)
- ✅ **Database Migration**: Completely migrated to PostgreSQL-only architecture (removed SQLite fallback)
- ✅ **Package Structure**: Reorganized entire codebase into professional modular architecture:
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
- ✅ **Production Ready**: Configured with Gunicorn, ProxyFix, and deployment settings
- ✅ **Application Factory**: Implemented proper Flask application factory pattern
- ✅ **Service Layer**: Separated business logic from routes into dedicated service classes
- ✅ **Repository Pattern**: Implemented for clean database access patterns

### Configuration Details
- **Server**: Gunicorn with reloading enabled for development
- **Database**: PostgreSQL with connection pooling and health checks (SQLite fallback for development)
- **Host Configuration**: Bound to 0.0.0.0:5000 to allow proxy access
- **Environment Secrets**: SESSION_SECRET and DATABASE_URL with development fallbacks
- **Workflow Status**: Running successfully on port 5000

### Environment Variables for Production
For production deployment, configure these environment variables:
- **SESSION_SECRET**: Secure session encryption key (auto-generated in development)
- **DATABASE_URL**: PostgreSQL connection string (defaults to SQLite in development)

### First-Time Setup
1. The application displays a login interface in Portuguese
2. **Admin user has been created and configured:**
   - An administrator account has been set up with secure credentials
   - Contact the system administrator for login credentials
   - Role: ADM (Administrator)
   - Status: Approved

3. To create additional admin users, run:
   ```bash
   python -c "from app import app, db; from models import User; with app.app_context(): admin = User.create_admin_user('username', 'email@empresa.com', 'secure_password'); db.session.add(admin); db.session.commit(); print('Admin created!')"
   ```

4. The system includes role-based access control with user approval workflow
5. All inventory management features are ready for use

### Ready for Publishing
The application is fully configured and ready to be published to production using Replit's deployment system.