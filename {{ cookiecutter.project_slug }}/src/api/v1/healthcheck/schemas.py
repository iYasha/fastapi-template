from api.v1.healthcheck.config import HealthCheck
from sdk.schemas import BaseSchema


class HealthCheckStatuses(BaseSchema):
    database_backend: str
    default_file_storage_health_check: str
    disk_usage: str
    memory_usage: str

    def is_all_success(self: 'HealthCheckStatuses') -> bool:
        return all(value == HealthCheck.OK_STATUS for _, value in self.__iter__())
