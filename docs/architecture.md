# Architecture Documentation

This document provides detailed information about the VroomSniffer architecture, design patterns, and implementation details.

## Service-Oriented Architecture

VroomSniffer is built with a service-oriented architecture that promotes separation of concerns through specialized service classes. The application follows a monolithic deployment model with a clean, layered architecture.

### Architecture Diagram

```
┌─────────────────────────────────┐       ┌─────────────────────┐
│            UI Layer             │       │      CLI Layer       │
│  (Streamlit Web Application)    │       │  (Command Line Tool) │
└───────────────┬─────────────────┘       └──────────┬──────────┘
                │                                     │
                ▼                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Services Provider                           │
│       (Centralized Service Factory and Dependency Manager)       │
└─────────────────────────────┬─────────────────────────────────┘
                             │
         ┌──────────────────┬┴───────────────┬─────────────────┐
         │                  │                │                 │
         ▼                  ▼                ▼                 ▼
┌─────────────────┐  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐
│ Storage Service │  │ Scraper Service│  │Notifier Svc  │  │Statistics Svc│
└────────┬────────┘  └────────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                    │                  │                 │
         ▼                    ▼                  ▼                 ▼
┌─────────────────┐  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐
│  JSON Storage   │  │Playwright      │  │Telegram Bot  │  │Analytics     │
│  (Data Files)   │  │(Scraper Engine)│  │(Notifications)│  │(Reporting)   │
└─────────────────┘  └────────────────┘  └──────────────┘  └──────────────┘
```

### Key Principles

- **Clean separation of concerns** with specialized services
- **Business logic in service layer**, not in UI or CLI
- **Dependency injection** through service provider
- **Singleton services** with consistent state across the application

### Key Architectural Components

1. **Entry Points Layer**
   - User interfaces that delegate all business logic to the service layer
   - UI (Streamlit web application) for browser-based interaction
   - CLI (Command-line interface) for terminal-based interaction

2. **Service Provider Layer**
   - Centralized access point for obtaining service instances
   - Manages service lifecycles and dependencies
   - Ensures consistent service state across the application

3. **Service Layer**
   - Contains the core business logic of the application
   - Implements domain operations as specialized service classes
   - Each service has a well-defined responsibility

4. **Infrastructure Layer**
   - Low-level components that support the service layer
   - Includes storage, scraping engine, notification systems

### Design Patterns

1. **Service Locator Pattern / Dependency Injection**
   - Implementation: `providers/services_provider.py`
   - Manages service instances and provides centralized access
   - Handles service dependencies automatically
   - Enables lazy initialization of services

2. **Singleton Pattern**
   - Implementation: Service instances in `services_provider.py`
   - Ensures only one instance of each service exists
   - Provides consistent state across the application

3. **Facade Pattern**
   - Implementation: Service classes encapsulate complex subsystems
   - Example: `ScraperService` provides a simplified interface to the scraping engine

4. **Repository Pattern**
   - Implementation: `StorageService` provides an abstraction over data storage
   - Isolates data access logic from business logic
   - Enables future changes to the storage mechanism

## Detailed Component Documentation

### Services Provider

The Services Provider (`providers/services_provider.py`) is responsible for:

1. **Service Creation**: Initializing service instances on demand
2. **Dependency Management**: Injecting required dependencies into services
3. **Singleton Management**: Ensuring only one instance of each service exists
4. **Lazy Loading**: Creating services only when they are needed

Implementation pattern:

```python
# Global service instances
_service_instance = None

def get_service():
    """Get or create the service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ServiceClass(get_dependency_service())
    return _service_instance
```

### Service Layer

The Service Layer contains specialized service classes for different domain concerns:

1. **StorageService**
   - Purpose: Data persistence and retrieval
   - Responsibilities: Load/save listings, manage caches, filter new listings
   - Location: `services/storage_service.py`

2. **ScraperService**
   - Purpose: Coordinate web scraping operations
   - Responsibilities: Run scraper, process listings, extract data
   - Location: `services/scraper_service.py`

3. **NotificationService**
   - Purpose: Send notifications about new listings
   - Responsibilities: Format messages, send to Telegram, handle errors
   - Location: `services/notification_service.py`

4. **UrlPoolService**
   - Purpose: Manage search URLs
   - Responsibilities: Save/load URLs, provide URL rotation
   - Location: `services/url_pool_service.py`

5. **StatisticsService**
   - Purpose: Generate analytics and reports
   - Responsibilities: Calculate metrics, trend analysis
   - Location: `services/statistics_service.py`

6. **SchedulerService**
   - Purpose: Handle scheduled operations
   - Responsibilities: Create/manage scheduled tasks
   - Location: `services/scheduler_service.py`

## Future Evolution

The current architecture is designed to evolve gracefully:

1. **Database Integration**
   - The storage service provides an abstraction layer
   - Can be extended to support database backends
   - JSON files can be replaced with proper database storage

2. **Scalability Enhancements**
   - Worker processes for parallel scraping
   - Message queues for asynchronous operations
   - Load balancing for distributed deployment

## Best Practices

1. **Keep Business Logic in Services**
   - UI and CLI should be thin and contain no business logic
   - All domain operations should be encapsulated in services

2. **Follow Dependency Injection**
   - Services should receive dependencies through constructor
   - Avoid direct instantiation of dependencies within services

3. **Maintain Service Boundaries**
   - Each service should have a clear, focused responsibility
   - Avoid creating dependencies between unrelated services

4. **Data Ownership**
   - Each data entity should have a clear owner service
   - Other services should access data through the owner service

5. **Error Handling**
   - Services should handle their own domain errors
   - Propagate appropriate errors to callers
   - Log detailed error information
