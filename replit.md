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
- **Development Server**: Built-in Flask development server with debugging
- **Static File Serving**: Flask static file handling for CSS and JavaScript assets