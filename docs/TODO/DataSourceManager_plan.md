# DataSourceManager Refactor/Enhancement Plan

**Date:** December 20, 2025

## Goals
- Ensure DataSourceManager supports dynamic registration/unregistration, lookup by name/type, and can return metadata about available sources.
- Add error handling for missing/unavailable sources if not already present.
- Consider singleton or dependency injection to avoid multiple conflicting instances.

## 1. Dynamic Registration/Unregistration & Lookup
- [x] `register_source(name, source)` already exists for registration.
- [ ] Add `unregister_source(name)` to allow removal of sources at runtime.
- [x] `get_source(name)` for lookup by name.
- [ ] Add `get_sources_by_type(type_name)` if sources are typed or categorized.
- [ ] Add `list_sources()` to return metadata (name, type, description) for all registered sources.

## 2. Error Handling for Missing/Unavailable Sources
- [x] `get_source(name)` returns None if not found (good practice).
- [ ] Add explicit error logging or raise a custom error (e.g., `DataSourceNotFoundError`) if a source is missing and is required for a workflow.
- [x] Error handling in `get_metrics()` is present for metrics collection.

## 3. Singleton/Dependency Injection
- **Singleton**: Ensures only one instance of DataSourceManager exists, preventing conflicting registrations or state. Can be implemented with a module-level instance or a singleton pattern.
- **Dependency Injection**: Pass the manager instance to components that need it, rather than using a global. This improves testability and modularity.
- [ ] Decide on singleton (current: global instance) or refactor to dependency injection for better testability.

## Recommendations
- Implement `unregister_source`, `list_sources`, and (optionally) `get_sources_by_type`.
- Add a custom error for missing sources if required.
- Document usage pattern (singleton vs. dependency injection) and refactor if needed for clarity and testability.
