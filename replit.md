# Equipment Inventory System

## Overview
This Flask-based Equipment Inventory System tracks IT equipment across various locations and organizations, with a focus on Brazilian business requirements (UF tracking, CNPJ management, Portuguese language). It supports equipment registration, status monitoring, location management, and detailed reporting, providing a comprehensive and scalable solution for inventory management. The system is designed for a professional and modern user experience.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework and UI/UX
The system uses a Flask application with a modular structure, SQLAlchemy ORM for database abstraction, and Flask-WTF for form handling. The frontend is built with Bootstrap 5 (dark theme responsive UI), Jinja2 templating, Plotly.js for interactive data visualization, and Font Awesome for iconography. The dashboard features a three-tier layout with Executive KPIs, interactive charts for compliance and analytics, and drill-down tables.

### Database Design
A PostgreSQL database is used as the primary data store, with a single table model for equipment data. It includes connection pooling with recycling and pre-ping for reliability. The database schema is automatically created on application startup, and sample data is pre-populated for testing.

### Data Management and Features
Key features include comprehensive form validation (server-side with WTForms), multi-criteria search and filtering, pagination for large datasets, and robust data import/export capabilities. Excel import supports template downloads and validation, while both Excel and PDF export functionalities are available, with security enhancements to use in-memory buffers instead of temporary files. The system also supports Brazilian Portuguese number formatting and dynamic handling of CNPJ values.

### Application Structure
The application follows a modular design with separated routes, models, forms, and utilities within the `inventory_app/` package. It uses an application factory pattern, blueprint-based routing, a service layer for business logic, and Flask-Migrate for database migrations. Environment configuration is flexible via environment variables, and static assets are managed efficiently.

### Security
Security features include CSRF protection, secure session management, and proxy support with Werkzeug's ProxyFix middleware. Export functionalities are implemented with security in mind, utilizing in-memory processing to prevent sensitive data leaks.

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: CSS framework (CDN)
- **Font Awesome 6.4.0**: Icon library (cdnjs.cloudflare.com)
- **Plotly.js**: Data visualization library (cdn.plot.ly)

### Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM integration
- **Flask-WTF**: Form handling
- **WTForms**: Form field types and validators
- **Pandas**: Data manipulation for exports
- **ReportLab**: PDF generation
- **Plotly**: Server-side chart generation
- **Werkzeug**: WSGI utilities and proxy middleware
- **Gunicorn**: Production WSGI server
- **Psycopg2**: PostgreSQL adapter

### Database Support
- **PostgreSQL**: Primary production database

### Deployment Infrastructure
- **Environment Variables**: `SESSION_SECRET`, `DATABASE_URL`
- **WSGI Compatibility**: Standard WSGI application structure
- **Replit Integration**: Fully configured for the Replit environment.