"""CDS Hooks service registry."""

from pathlib import Path

import yaml

from ..config.settings import CDSHooksSettings, CDSServiceConfig
from ..models.discovery import CDSServiceDescriptor, DiscoveryResponse


class ServiceRegistry:
    """Registry for CDS Hook services."""

    def __init__(self, settings: CDSHooksSettings):
        self._settings = settings
        self._services: dict[str, CDSServiceConfig] = {}
        self._load_services()

    def _load_services(self) -> None:
        """Load services from configuration file."""
        config_path = Path(self._settings.services_config_path)
        if not config_path.exists():
            return

        with open(config_path) as f:
            config = yaml.safe_load(f)

        if not config:
            return

        for service_data in config.get("services") or []:
            service = CDSServiceConfig(**service_data)
            if service.enabled:
                self._services[service.id] = service

    def get_service(self, service_id: str) -> CDSServiceConfig | None:
        """Get service configuration by ID."""
        return self._services.get(service_id)

    def list_services(self) -> list[CDSServiceConfig]:
        """List all registered services."""
        return list(self._services.values())

    def get_discovery_response(self) -> DiscoveryResponse:
        """Generate discovery response."""
        descriptors = []
        for service in self._services.values():
            descriptor = CDSServiceDescriptor(
                hook=service.hook,
                id=service.id,
                title=service.title,
                description=service.description,
                prefetch=service.prefetch if service.prefetch else None,
                usageRequirements=service.usageRequirements,
            )
            descriptors.append(descriptor)
        return DiscoveryResponse(services=descriptors)

    def register_service(self, service: CDSServiceConfig) -> None:
        """Dynamically register a service."""
        self._services[service.id] = service

    def unregister_service(self, service_id: str) -> bool:
        """Remove a service from the registry."""
        if service_id in self._services:
            del self._services[service_id]
            return True
        return False

    def reload(self) -> None:
        """Reload services from configuration file."""
        self._services.clear()
        self._load_services()
