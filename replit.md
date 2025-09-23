# Overview

Hurtrock Music Store is a Flask-based e-commerce web application specializing in musical instruments and accessories. The platform provides a complete online shopping experience with user authentication, product catalog management, shopping cart functionality, and Stripe payment integration. The application targets Indonesian customers with Indonesian language content and features a modern vintage orange-black themed interface.

## Recent Changes

- **September 23, 2025**: Project rebranding and client customization by fajarjulyana
  - **Rebranding**: Removed all Replit-specific references and replaced with generic domain handling
    - Changed REPLIT_DOMAINS to DOMAINS environment variable for generic hosting
    - Updated Django settings to use dynamic domain configuration
    - Replaced REPLIT_ENVIRONMENT with IS_PRODUCTION for generic environment detection
    - Made DEBUG configurable via DJANGO_DEBUG environment variable
  - **Fixed floating chat**: Product tags in chat are now clickable and functional
    - Replaced inline onclick with proper event listeners
    - Added data-product-url attributes for reliable click handling
    - Fixed chat WebSocket connection for cloud environments
  - **Implemented product image carousel**: Enhanced product detail pages with full carousel functionality
    - Added left/right arrow navigation for product images
    - Implemented image counter (1/3, 2/3, etc.)
    - Added keyboard navigation support (arrow keys)
    - Click-to-next functionality on main image
    - Synchronized thumbnail gallery with carousel navigation
    - Responsive design for mobile and desktop
  - **Security improvements**: Added production-ready configurations
    - Made Django DEBUG environment-configurable for secure production deployment
    - Enhanced CORS and ALLOWED_HOSTS security based on DEBUG state
    - Updated Flask production detection to use generic environment variables
  - Client deployment ready: All platform-specific code removed for generic hosting

- **September 23, 2025**: Fresh GitHub import successfully configured for environment
  - Fixed JWT security vulnerability by separating JWT_SECRET_KEY from SESSION_SECRET
  - Installed all required Python dependencies (Flask, SQLAlchemy, Django, Stripe, etc.)
  - Configured Flask Server workflow running on port 5000 with proper host configuration (0.0.0.0)
  - Set up PostgreSQL database connection using environment variables
  - Verified database initialization with automatic admin user and sample data creation
  - Configured deployment settings for autoscale production deployment
  - Application is fully functional with all core features working
  - Default admin user: admin@hurtrock.com (password: admin123)
  - Django chat service temporarily disabled for initial setup stability

- **September 22, 2025**: Successfully re-imported and fully configured project in Replit environment
  - Configured PostgreSQL database connection (DATABASE_URL environment variable set)
  - Installed all Python dependencies using Replit's package manager
  - Set up Flask Server workflow running on port 5000 with proper host configuration (0.0.0.0)  
  - Created database tables and populated with sample data (categories, products, suppliers, shipping services)
  - Added missing hero image for homepage (music store interior)
  - Configured deployment settings for autoscale production deployment  
  - Verified application is fully functional with all core features working
  - Default admin user: admin@hurtrock.com (password: admin123)

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with a responsive Bootstrap 5 UI framework
- **Theme System**: Light/dark mode toggle with CSS custom properties for theme switching
- **User Interface**: Modern vintage design with orange-black color scheme, glass morphism effects, and mobile-first responsive design
- **JavaScript Features**: Real-time search functionality, theme persistence, and interactive cart management
- **Asset Management**: Static files served via Flask's static file handling

## Backend Architecture
- **Web Framework**: Flask with modular structure separating models, routes, and configuration
- **Authentication**: Flask-Login for session management with secure cookie configuration for production environments
- **Security**: CSRF protection via Flask-WTF, secure session cookies, and password hashing using Werkzeug
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy integration using declarative base model approach
- **Migration Management**: Flask-Migrate for database schema versioning and updates

## Data Storage Solutions
- **Primary Database**: PostgreSQL (configured via DATABASE_URL environment variable)
- **Connection Management**: Connection pooling with automatic reconnection and 300-second pool recycle
- **Session Storage**: Flask sessions for user state management and shopping cart persistence

## Authentication and Authorization
- **User Management**: Custom User model with email-based authentication and password hashing
- **Session Security**: HTTPS-only cookies, HTTP-only flags, and SameSite protection for CSRF prevention
- **Access Control**: Login-required decorators for protected routes and user-specific data access

## Core Data Models
- **User Model**: Handles customer accounts with profile information and relationship to orders/cart
- **Product Model**: Central product catalog with category relationships, pricing, and inventory management
- **Category Model**: Product categorization system with hierarchical organization
- **Cart Model**: Shopping cart functionality with item quantity management and subtotal calculations
- **Order Model**: Order processing and tracking with status management workflow

# External Dependencies

## Payment Processing
- **Stripe Integration**: Complete payment processing with Stripe API for secure credit card transactions
- **Payment Flow**: Checkout process with order confirmation and payment success handling

## Third-Party Libraries
- **Bootstrap 5**: Frontend CSS framework for responsive design and UI components
- **Font Awesome**: Icon library for consistent iconography throughout the application
- **jQuery**: JavaScript library for enhanced interactivity and AJAX functionality

## Environment Configuration
- **Required Environment Variables**: SESSION_SECRET for Flask sessions, DATABASE_URL for PostgreSQL connection, STRIPE_SECRET_KEY for payment processing
- **Security Configuration**: Production-ready security settings with HTTPS enforcement and secure cookie configuration

## Sample Data System
- **Data Population**: Automated sample data creation script for categories and products to facilitate development and testing
- **Image Handling**: Placeholder image system with fallback URLs for missing product images