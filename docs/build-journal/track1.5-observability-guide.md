# Track 1.5: Structured Observability and Tracing

## Implementation Guide - Phase 3.2

**Status:** 📋 Ready for Implementation  
**Priority:** Medium (Post-MVP)  
**Dependencies:** Track 1.1-1.4 Complete

---

## Overview

Add structured logging, request tracing, and observability to correlate frontend and backend operations.

---

## 1. Structured JSON Logging

### Backend Logger Configuration

**File:** `backend/app/core/logging_config.py`

```python
import logging
import json
from datetime import datetime
from contextvars import ContextVar
from typing import Optional

# Context variable for request tracking
request_context: ContextVar[dict] = ContextVar('request_context', default={})

class StructuredJSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Get request context
        ctx = request_context.get({})
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            
            # Request context
            "request_id": ctx.get('request_id'),
            "task_id": ctx.get('task_id'),
            "content_type": ctx.get('content_type'),
            "user_id": ctx.get('user_id'),
            "route": ctx.get('route'),
            
            # Performance metrics
            "duration_ms": ctx.get('duration_ms'),
            
            # Validation context
            "validator_valid": ctx.get('validator_valid'),
            "missing_fields_count": ctx.get('missing_fields_count'),
            
            # Export context
            "export_format": ctx.get('export_format'),
            "export_size_bytes": ctx.get('export_size_bytes'),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}
        
        return json.dumps(log_data)


def configure_logging():
    """Configure application-wide structured logging"""
    
    # Create formatter
    formatter = StructuredJSONFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler (rotate daily)
    from logging.handlers import TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        filename='logs/aura.log',
        when='midnight',
        interval=1,
        backupCount=30
    )
    file_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return root_logger
```

### Request Context Middleware

**File:** `backend/app/core/request_context_middleware.py`

```python
import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging_config import request_context

class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to track request context for logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        
        # Set context
        ctx = {
            'request_id': request_id,
            'route': request.url.path,
            'method': request.method,
        }
        
        # Add user ID if authenticated
        if hasattr(request.state, 'user'):
            ctx['user_id'] = request.state.user.id
        
        request_context.set(ctx)
        
        # Track timing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        ctx['duration_ms'] = round(duration_ms, 2)
        request_context.set(ctx)
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Duration-Ms'] = str(round(duration_ms, 2))
        
        return response
```

---

## 2. Request ID Correlation

### Frontend Logger

**File:** `aura-client/src/utils/logger.ts`

```typescript
/**
 * Structured logger with request ID correlation
 */

export class Logger {
  private static requestId: string | null = null;
  
  static setRequestId(id: string) {
    this.requestId = id;
  }
  
  static log(group: string, message: string, data?: any) {
    const logData = {
      timestamp: new Date().toISOString(),
      group: `[${group}]`,
      message,
      request_id: this.requestId,
      ...data
    };
    
    console.group(`${logData.group} ${message}`);
    console.log('Request ID:', this.requestId);
    if (data) console.log('Data:', data);
    console.groupEnd();
  }
  
  static error(group: string, message: string, error?: any) {
    console.error(`[${group}] ${message}`, {
      request_id: this.requestId,
      error
    });
  }
}

// Usage in API calls
export async function fetchWithLogging(url: string, options: RequestInit) {
  const response = await fetch(url, options);
  
  // Extract request ID from response
  const requestId = response.headers.get('X-Request-ID');
  if (requestId) {
    Logger.setRequestId(requestId);
  }
  
  return response;
}
```

---

## 3. OpenTelemetry Integration (Optional)

### Backend Tracing

**File:** `backend/app/core/tracing.py`

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

def configure_tracing():
    """Configure OpenTelemetry tracing"""
    
    # Create tracer provider
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)
    
    # Configure Jaeger exporter (if enabled)
    if os.getenv('ENABLE_TRACING', 'false').lower() == 'true':
        jaeger_exporter = JaegerExporter(
            agent_host_name=os.getenv('JAEGER_HOST', 'localhost'),
            agent_port=int(os.getenv('JAEGER_PORT', '6831')),
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        tracer_provider.add_span_processor(span_processor)
    
    return trace.get_tracer(__name__)


# Usage in validators
tracer = configure_tracing()

def validate_cma_report(payload: dict):
    with tracer.start_as_current_span("validate_cma_report") as span:
        span.set_attribute("content_type", "CMA_REPORT")
        span.set_attribute("payload_size", len(payload))
        
        # Validation logic...
        result = _do_validation(payload)
        
        span.set_attribute("valid", result.valid)
        span.set_attribute("missing_fields_count", len(result.missing_fields))
        
        return result
```

---

## 4. Metrics Dashboard

### Prometheus Metrics (Optional)

**File:** `backend/app/core/metrics.py`

```python
from prometheus_client import Counter, Histogram, Gauge

# Validation metrics
validation_total = Counter(
    'aura_validation_total',
    'Total validation attempts',
    ['content_type', 'valid']
)

validation_duration = Histogram(
    'aura_validation_duration_seconds',
    'Validation duration',
    ['content_type']
)

# Export metrics
export_total = Counter(
    'aura_export_total',
    'Total export attempts',
    ['content_type', 'format', 'status']
)

export_duration = Histogram(
    'aura_export_duration_seconds',
    'Export generation duration',
    ['content_type', 'format']
)

export_size = Histogram(
    'aura_export_size_bytes',
    'Export file size',
    ['content_type', 'format']
)

# Task sync metrics
task_sync_requests = Counter(
    'aura_task_sync_requests_total',
    'Total task sync requests'
)

task_sync_tasks_returned = Histogram(
    'aura_task_sync_tasks_count',
    'Number of tasks returned per sync'
)
```

---

## 5. Log Aggregation

### Recommended Setup

1. **Development:** Console logs with JSON formatting
2. **Staging:** ELK Stack (Elasticsearch, Logstash, Kibana)
3. **Production:** DataDog, New Relic, or CloudWatch

### Example Queries

```
# Find all validation failures in last hour
level:ERROR AND validator_valid:false AND @timestamp:[now-1h TO now]

# Track export performance
route:/api/v1/export/* AND duration_ms:>5000

# Correlation: Find all logs for a request
request_id:"abc-123-def"
```

---

## 6. Environment Configuration

**File:** `.env`

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # or 'text' for development
LOG_FILE=logs/aura.log

# Tracing
ENABLE_TRACING=false
JAEGER_HOST=localhost
JAEGER_PORT=6831

# Metrics
ENABLE_METRICS=false
METRICS_PORT=9090
```

---

## 7. Dashboard Configuration

### Grafana Dashboard (JSON)

```json
{
  "title": "Aura Content Engine",
  "panels": [
    {
      "title": "Validation Success Rate",
      "targets": [
        {
          "expr": "sum(rate(aura_validation_total{valid=\"true\"}[5m])) / sum(rate(aura_validation_total[5m]))"
        }
      ]
    },
    {
      "title": "Export Duration (p95)",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, rate(aura_export_duration_seconds_bucket[5m]))"
        }
      ]
    },
    {
      "title": "Task Sync Errors",
      "targets": [
        {
          "expr": "rate(aura_task_sync_requests_total{status=\"error\"}[5m])"
        }
      ]
    }
  ]
}
```

---

## Implementation Priority

### MVP (Required)
- ✅ Structured JSON logging
- ✅ Request ID correlation
- ✅ Frontend/backend log alignment

### Post-MVP (Nice to Have)
- ⏳ OpenTelemetry tracing
- ⏳ Prometheus metrics
- ⏳ Grafana dashboards
- ⏳ Alert rules

---

## Testing

```python
# Test structured logging
def test_structured_logging():
    logger = logging.getLogger('test')
    
    # Set context
    request_context.set({
        'request_id': 'test-123',
        'task_id': 'task-456',
        'content_type': 'CMA_REPORT'
    })
    
    # Log message
    logger.info("Test message")
    
    # Verify JSON output contains context
    # (capture and parse log output)
```

---

## Next Steps

1. Implement structured logging middleware
2. Add request ID to all API responses
3. Update frontend logger to use request IDs
4. Add basic metrics (validation, export)
5. Set up log aggregation (staging/production)
6. Create initial Grafana dashboards

---

**Last Updated:** 2025-10-10T08:30:00Z  
**Status:** Ready for Implementation  
**Track:** 1.5 Observability
