#!/usr/bin/env python3
"""
Generate Test Metrics with Anomalies
Creates synthetic time series data for testing SAIMon
"""

import time
import random
import argparse
from datetime import datetime
from prometheus_client import start_http_server, Gauge

# Create metrics
cpu_usage = Gauge('saimon_test_cpu_usage', 'Simulated CPU usage percentage')
memory_usage = Gauge('saimon_test_memory_usage', 'Simulated memory usage in MB')
response_time = Gauge('saimon_test_response_time', 'Simulated API response time in ms')
error_rate = Gauge('saimon_test_error_rate', 'Simulated error rate')

def generate_normal_cpu():
    """Generate normal CPU usage (50-70%)"""
    return random.gauss(60, 5)

def generate_spike_cpu():
    """Generate CPU spike (90-100%)"""
    return random.gauss(95, 3)

def generate_normal_memory():
    """Generate normal memory usage (2000-4000 MB)"""
    return random.gauss(3000, 500)

def generate_spike_memory():
    """Generate memory spike (7000-9000 MB)"""
    return random.gauss(8000, 500)

def generate_normal_response_time():
    """Generate normal response time (10-50ms)"""
    return max(5, random.gauss(30, 10))

def generate_slow_response_time():
    """Generate slow response time (500-1000ms)"""
    return random.gauss(750, 150)

def generate_normal_error_rate():
    """Generate normal error rate (0-2%)"""
    return max(0, random.gauss(1, 0.5))

def generate_high_error_rate():
    """Generate high error rate (10-20%)"""
    return random.gauss(15, 3)

def main():
    parser = argparse.ArgumentParser(description='Generate test metrics with anomalies')
    parser.add_argument('--port', type=int, default=8001, help='Port to expose metrics')
    parser.add_argument('--interval', type=int, default=5, help='Scrape interval in seconds')
    parser.add_argument('--anomaly-rate', type=float, default=0.1, help='Probability of anomaly (0-1)')
    parser.add_argument('--duration', type=int, default=None, help='Duration to run (seconds), default=forever')
    
    args = parser.parse_args()
    
    # Start metrics server
    start_http_server(args.port)
    print(f"📊 Generating test metrics on http://localhost:{args.port}/metrics")
    print(f"⏱️  Interval: {args.interval}s, Anomaly Rate: {args.anomaly_rate*100}%")
    print(f"🔥 Press Ctrl+C to stop\n")
    
    start_time = time.time()
    iteration = 0
    
    try:
        while True:
            iteration += 1
            is_anomaly = random.random() < args.anomaly_rate
            
            # Generate metrics
            if is_anomaly:
                anomaly_type = random.choice(['cpu_spike', 'memory_spike', 'slow_response', 'high_errors'])
                
                if anomaly_type == 'cpu_spike':
                    cpu = generate_spike_cpu()
                    memory = generate_normal_memory()
                    response = generate_normal_response_time()
                    errors = generate_normal_error_rate()
                    print(f"🔴 [{datetime.now().strftime('%H:%M:%S')}] ANOMALY: CPU Spike ({cpu:.1f}%)")
                
                elif anomaly_type == 'memory_spike':
                    cpu = generate_normal_cpu()
                    memory = generate_spike_memory()
                    response = generate_normal_response_time()
                    errors = generate_normal_error_rate()
                    print(f"🔴 [{datetime.now().strftime('%H:%M:%S')}] ANOMALY: Memory Spike ({memory:.0f} MB)")
                
                elif anomaly_type == 'slow_response':
                    cpu = generate_normal_cpu()
                    memory = generate_normal_memory()
                    response = generate_slow_response_time()
                    errors = generate_normal_error_rate()
                    print(f"🔴 [{datetime.now().strftime('%H:%M:%S')}] ANOMALY: Slow Response ({response:.0f} ms)")
                
                else:  # high_errors
                    cpu = generate_normal_cpu()
                    memory = generate_normal_memory()
                    response = generate_normal_response_time()
                    errors = generate_high_error_rate()
                    print(f"🔴 [{datetime.now().strftime('%H:%M:%S')}] ANOMALY: High Errors ({errors:.1f}%)")
            
            else:
                # Normal behavior
                cpu = generate_normal_cpu()
                memory = generate_normal_memory()
                response = generate_normal_response_time()
                errors = generate_normal_error_rate()
                
                if iteration % 20 == 0:  # Print status every 20 iterations
                    print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Normal: "
                          f"CPU={cpu:.1f}%, Mem={memory:.0f}MB, "
                          f"RT={response:.0f}ms, Err={errors:.1f}%")
            
            # Update metrics
            cpu_usage.set(max(0, min(100, cpu)))
            memory_usage.set(max(0, memory))
            response_time.set(max(0, response))
            error_rate.set(max(0, min(100, errors)))
            
            # Check duration
            if args.duration and (time.time() - start_time) >= args.duration:
                print(f"\n⏰ Duration limit reached ({args.duration}s)")
                break
            
            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        print(f"\n\n👋 Stopped after {iteration} iterations")
        print(f"Total runtime: {int(time.time() - start_time)}s")

if __name__ == "__main__":
    main()
