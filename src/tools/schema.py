from pydantic import BaseModel, Field

class GetLogsInput(BaseModel):
    service: str = Field(description="The name of the service to fetch logs for")
    timeframe: str = Field(description="Timeframe for the logs, e.g., 'last_5_minutes'")

class GetMetricsInput(BaseModel):
    service: str = Field(description="The name of the service to fetch metrics for")

class SimulateRestartInput(BaseModel):
    service: str = Field(description="The name of the service to restart")

class SimulateScaleInput(BaseModel):
    service: str = Field(description="The name of the service to scale")
    replicas: int = Field(description="The target number of replicas")

class GetDependencyGraphInput(BaseModel):
    service: str = Field(description="The service to fetch dependencies for")
