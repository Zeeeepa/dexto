# Performance Optimization Guide

Comprehensive guide for optimizing Voice Automation Hub performance.

## Table of Contents
- [Performance Monitoring](#performance-monitoring)
- [Backend Optimization](#backend-optimization)
- [Frontend Optimization](#frontend-optimization)
- [Database & Storage](#database--storage)
- [Caching Strategies](#caching-strategies)
- [Scaling](#scaling)

## Performance Monitoring

### Built-in Metrics
Access real-time metrics at `/api/metrics`:

```python
{
  "counters": {
    "requests.get": 1234,
    "requests.post": 567,
    "responses.200": 1500,
    "responses.500": 2
  },
  "gauges": {
    "active_workflows": 5,
    "memory_usage_mb": 256
  },
  "timers": {
    "request_duration": {
      "count": 1801,
      "min": 0.001,
      "max": 2.345,
      "avg": 0.123,
      "p50": 0.100,
      "p95": 0.450,
      "p99": 1.200
    }
  }
}
```

### Performance Tracking
```python
from app.monitoring import metrics

# Track custom metrics
metrics.increment("custom_event")
metrics.set_gauge("queue_size", 10)
metrics.record_value("processing_time", 0.5)

# Use timer context manager
with metrics.timer("operation_name"):
    # Your code here
    pass
```

### Health Checks
Monitor system health at `/api/health/detailed`:
```json
{
  "status": "healthy",
  "checks": {
    "error_rate": {
      "status": "healthy",
      "value": 0.02,
      "threshold": 0.1
    },
    "request_volume": {
      "status": "healthy",
      "value": 100
    }
  }
}
```

## Backend Optimization

### Async Operations
Always use async/await for I/O operations:

```python
# ❌ Bad - Blocking
def fetch_data():
    response = requests.get(url)
    return response.json()

# ✅ Good - Non-blocking
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### Connection Pooling
Configure connection limits:

```python
# Configure httpx client
client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100
    ),
    timeout=httpx.Timeout(30.0)
)
```

### Request Batching
Batch multiple requests:

```python
async def process_batch(items):
    """Process items in batches."""
    batch_size = 10
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await asyncio.gather(
            *[process_item(item) for item in batch]
        )
        results.extend(batch_results)
    
    return results
```

### Error Handling
Use circuit breaker pattern:

```python
from app.error_handling import CircuitBreaker

circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60
)

def call_external_service():
    return circuit_breaker.call(external_api_call)
```

### Response Compression
Enable gzip compression in Nginx:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1024;
```

## Frontend Optimization

### Code Splitting
Use dynamic imports:

```typescript
// ❌ Bad - Load everything upfront
import { HeavyComponent } from './HeavyComponent';

// ✅ Good - Load on demand
const HeavyComponent = lazy(() => import('./HeavyComponent'));
```

### Memoization
Optimize re-renders:

```typescript
// Memoize expensive calculations
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// Memoize callbacks
const handleClick = useCallback(() => {
  doSomething(value);
}, [value]);

// Memoize components
const MemoizedComponent = React.memo(MyComponent);
```

### Virtual Scrolling
For long lists:

```typescript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={items.length}
  itemSize={50}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>{items[index]}</div>
  )}
</FixedSizeList>
```

### Asset Optimization
- Compress images (WebP format)
- Lazy load images
- Use CDN for static assets
- Minify CSS/JS in production

### Bundle Size
Monitor bundle size:

```bash
npm run build -- --stats
npx webpack-bundle-analyzer dist/stats.json
```

## Database & Storage

### Memory Store Optimization
Configure memory limits:

```python
from app.memory_store import MemoryStore

# Limit thread history
store = MemoryStore(
    max_threads=1000,
    max_messages_per_thread=100
)
```

### Pagination
Always paginate large datasets:

```python
@app.get("/api/items")
async def list_items(page: int = 1, limit: int = 50):
    """List items with pagination."""
    offset = (page - 1) * limit
    items = get_items(offset=offset, limit=limit)
    
    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": get_total_count()
    }
```

### Batch Operations
Batch database operations:

```python
# ❌ Bad - Multiple individual operations
for item in items:
    store.add_message(thread_id, item)

# ✅ Good - Single batch operation
store.add_messages_batch(thread_id, items)
```

## Caching Strategies

### Response Caching
Cache expensive computations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param):
    """Cache results of expensive calculation."""
    # Expensive operation
    return result
```

### Redis Caching
For distributed caching:

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)

def get_cached_data(key):
    """Get data from cache."""
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    # Fetch and cache
    data = fetch_data()
    redis_client.setex(key, 3600, json.dumps(data))
    return data
```

### HTTP Caching
Configure cache headers:

```python
@app.get("/api/static-data")
async def get_static_data(response: Response):
    """Serve with cache headers."""
    response.headers["Cache-Control"] = "public, max-age=3600"
    return {"data": "static content"}
```

## Scaling

### Horizontal Scaling
Run multiple instances:

```bash
# Docker Compose scaling
docker-compose up --scale backend=3
```

### Load Balancing
Nginx configuration:

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

### Worker Processes
Configure Uvicorn workers:

```bash
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Background Tasks
Offload heavy tasks:

```python
from fastapi import BackgroundTasks

@app.post("/api/heavy-task")
async def trigger_task(background_tasks: BackgroundTasks):
    """Trigger background task."""
    background_tasks.add_task(process_heavy_task)
    return {"status": "processing"}
```

## Performance Checklist

### Backend
- [ ] Use async/await for I/O
- [ ] Enable response compression
- [ ] Implement connection pooling
- [ ] Add request timeout limits
- [ ] Use circuit breakers
- [ ] Implement rate limiting
- [ ] Enable HTTP/2
- [ ] Configure worker processes

### Frontend
- [ ] Enable code splitting
- [ ] Implement lazy loading
- [ ] Use memoization
- [ ] Optimize images
- [ ] Minify assets
- [ ] Enable gzip
- [ ] Use CDN
- [ ] Implement virtual scrolling

### Database
- [ ] Add pagination
- [ ] Implement caching
- [ ] Optimize queries
- [ ] Add indexes
- [ ] Use batch operations
- [ ] Limit result sizes

### Monitoring
- [ ] Track key metrics
- [ ] Set up alerts
- [ ] Monitor error rates
- [ ] Track response times
- [ ] Monitor resource usage
- [ ] Review logs regularly

## Performance Testing

### Load Testing
Use tools like `locust`:

```python
# locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def create_workflow(self):
        self.client.post("/api/workflows", json={
            "task": "Test workflow"
        })
    
    @task(2)
    def list_workflows(self):
        self.client.get("/api/workflows")
```

Run test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

### Profiling
Profile Python code:

```bash
python -m cProfile -o profile.stats app/main.py
python -m pstats profile.stats
```

### Benchmarking
Use `hyperfine` for benchmarking:

```bash
hyperfine 'curl http://localhost:8000/api/health'
```

## Troubleshooting

### High Response Times
1. Check `/api/metrics` for slow endpoints
2. Review error logs
3. Profile code
4. Check database queries
5. Monitor network latency

### High Memory Usage
1. Check for memory leaks
2. Review cache sizes
3. Limit result set sizes
4. Use generators for large datasets
5. Monitor object creation

### High CPU Usage
1. Profile CPU usage
2. Optimize algorithms
3. Use caching
4. Implement batch processing
5. Consider async operations

## Additional Resources

- [FastAPI Performance](https://fastapi.tiangolo.com/deployment/concepts/)
- [React Performance](https://react.dev/learn/render-and-commit)
- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [Web Performance](https://web.dev/performance/)

