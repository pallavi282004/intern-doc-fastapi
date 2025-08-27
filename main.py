from fastapi import FastAPI
import logging
import time
import random

from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource   # 👈 NEW

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# OpenTelemetry Tracing with service name
resource = Resource.create({"service.name": "fastapi"})  # 👈 important
trace.set_tracer_provider(TracerProvider(resource=resource))

otlp_exporter = OTLPSpanExporter(
    endpoint="http://tempo:4317",  # gRPC
    insecure=True
)

trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

FastAPIInstrumentor.instrument_app(app)

@app.get("/hello")
async def hello():
    start = time.time()
    sleep_time = random.uniform(0.1, 0.5)
    time.sleep(sleep_time)
    duration = time.time() - start
    logger.info(f"/hello called, duration={duration:.3f}s")
    return {"message": "Hello, world!", "processing_time": duration}

