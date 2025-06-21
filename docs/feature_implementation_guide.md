# Feature Implementation Guide

This guide outlines how to add new features to VroomSniffer while maintaining the clean architecture and separation of concerns.

## Architecture Overview

VroomSniffer follows a service-oriented architecture with clean separation of concerns:

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

## Step-by-Step Implementation Guide

### 1. Define the Service Layer (Business Logic)

Create a new service class in the `services` directory:

```python
# services/your_new_service.py
class YourNewService:
    def __init__(self, dependency_service=None):
        # Initialize with dependencies
        if dependency_service:
            self.dependency_service = dependency_service
        else:
            # Import here to avoid circular imports
            from providers.services_provider import get_dependency_service
            self.dependency_service = get_dependency_service()
    
    def your_new_feature_method(self, param1, param2):
        # Implement business logic here
        result = self.dependency_service.some_method()
        # Process result
        return processed_result
```

### 2. Add to Services Provider

Update the services provider to include your new service:

```python
# providers/services_provider.py
from services.your_new_service import YourNewService

# Add singleton instance variable
_your_new_service = None

def get_your_new_service():
    """Get or create the your new service instance."""
    global _your_new_service
    if _your_new_service is None:
        _your_new_service = YourNewService(get_dependency_service())
    return _your_new_service
```

### 3. Expose in UI Layer (if needed)

Create or update a UI page to use your new service:

```python
# ui/pages/your_feature_page.py
import streamlit as st
from providers.services_provider import get_your_new_service

# Initialize service
your_new_service = get_your_new_service()

def your_feature_ui():
    st.title("Your New Feature")
    
    # UI controls
    param1 = st.text_input("Parameter 1")
    param2 = st.slider("Parameter 2", 0, 100)
    
    if st.button("Run Feature"):
        # Call service method
        result = your_new_service.your_new_feature_method(param1, param2)
        
        # Display result
        st.success(f"Feature completed! Result: {result}")
```

### 4. Expose in CLI Layer (if needed)

Update the CLI to include your new feature:

```python
# In cli/main.py add:
def your_feature_command(args):
    """Implement your new feature command"""
    from providers.services_provider import get_your_new_service
    
    your_new_service = get_your_new_service()
    result = your_new_service.your_new_feature_method(args.param1, args.param2)
    
    print(f"Feature completed! Result: {result}")

# In parse_args function, add:
your_feature_parser = subparsers.add_parser("your-feature", help="Run your new feature")
your_feature_parser.add_argument("param1", help="First parameter")
your_feature_parser.add_argument("--param2", type=int, default=50, help="Second parameter")
your_feature_parser.set_defaults(func=your_feature_command)
```

### 5. Add Storage (if needed)

If your feature requires persistent storage:

1. Define data structure and storage needs
2. Use the existing storage service or extend it
3. Consider where to store data (new or existing JSON files)

Example:
```python
# In your service method
def save_feature_data(self, data):
    from providers.services_provider import get_storage_service
    storage_service = get_storage_service()
    
    # Either use existing methods
    storage_service.save_listings(data)
    
    # Or add custom storage logic
    storage_path = Path(__file__).parent.parent / "storage" / "your_feature_data.json"
    storage_service.save_cache(data, str(storage_path))
```

### 6. Testing

Create appropriate tests for your feature:

1. Unit tests for service methods
2. Integration tests for service interactions
3. UI or CLI tests as needed

### 7. Documentation

Update documentation:

1. Add brief mention of the feature in the README.md
2. Document the service API
3. Update technical documentation if necessary
4. Provide usage examples

## Design Principles to Follow

1. **Separation of Concerns**: Business logic belongs in services, not in UI or CLI
2. **Dependency Injection**: Services should receive dependencies through constructor or provider
3. **Single Responsibility**: Each service should have a focused purpose
4. **Don't Repeat Yourself**: Reuse existing services and code when applicable
5. **Testability**: Design services to be easily testable in isolation

## Example: Adding a Report Generation Feature

Here's a concrete example of adding a report generation feature:

1. **Create the service**:
   - `services/report_service.py`
   - Implements methods like `generate_daily_report()`, `export_to_csv()`, etc.

2. **Update the provider**:
   - Add `get_report_service()` to `providers/services_provider.py`
   - Handle dependencies (e.g., needs `storage_service`)

3. **Add UI components**:
   - Create `ui/pages/reports.py` with reporting UI
   - Add report generation controls and visualization

4. **Add CLI commands**:
   - Add `report` command to `cli/main.py`
   - Implement options like `--daily`, `--weekly`, `--csv`, etc.

5. **Storage**:
   - Use `storage/reports/` directory for report outputs
   - Implement storage methods for report data

By following these steps, your new feature will integrate seamlessly with the existing architecture and maintain the clean separation of concerns.
