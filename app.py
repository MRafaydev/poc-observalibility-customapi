from flask import Flask
from prometheus_client import Counter, Histogram, make_wsgi_app
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
from prometheus_client import multiprocess
import requests
import time

app = Flask(__name__)

# # Define Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'Total number of requests')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency in seconds')


class CustomCollector(object):
    def __init__(self):
        pass
        
    def collect(self):
        # Create a Gauge metric for the returned value
        value_gauge = GaugeMetricFamily('returned_value', 'The returned value', labels=['value'])
        
        # Determine the value to return based on the current time
        current_time = int(time.time()) % 60
        if current_time < 30:
            value = 1
        else:
            value = 0
        
        # Set the value of the Gauge metric
        value_gauge.add_metric([str(value)], value)
        
        # Create a Counter metric for the total number of requests
        request_counter = CounterMetricFamily('total_requests', 'Total number of requests', labels=['method', 'endpoint'])
        request_counter.add_metric(['GET', '/'], REQUEST_COUNT._value.get())
        request_counter.add_metric(['GET', '/metrics'], 1)
        
        # Yield the metrics to Prometheus
        yield value_gauge
        yield request_counter

# Register the custom collector with Prometheus
REGISTRY.register(CustomCollector())

@app.route('/')
def hello():
    # Increment request count
    REQUEST_COUNT.inc()
    
    # Measure request latency
    with REQUEST_LATENCY.time():
        # Determine the value to return based on the current time
        current_time = int(time.time()) % 60
        if current_time < 30:
            value = 1
            print(value)
        else:
            value = 0
            print(value)
    return f'Hello World {value}'

# Add Prometheus metrics endpoint
@app.route('/metrics')
def metrics():
    return make_wsgi_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
