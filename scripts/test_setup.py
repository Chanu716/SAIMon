#!/usr/bin/env python3
"""
SAIMon Setup Verification Script
Tests all components and connections
"""

import sys
import httpx
from datetime import datetime

def print_status(message, status):
    """Print colored status message"""
    colors = {
        'OK': '\033[92m',      # Green
        'FAIL': '\033[91m',    # Red
        'WARN': '\033[93m',    # Yellow
        'INFO': '\033[94m'     # Blue
    }
    end_color = '\033[0m'
    print(f"[{colors.get(status, '')}{status}{end_color}] {message}")

def test_prometheus():
    """Test Prometheus connectivity"""
    try:
        response = httpx.get('http://localhost:9090/-/healthy', timeout=5)
        if response.status_code == 200:
            print_status("Prometheus is healthy", "OK")
            return True
        else:
            print_status(f"Prometheus returned status {response.status_code}", "FAIL")
            return False
    except Exception as e:
        print_status(f"Prometheus connection failed: {e}", "FAIL")
        return False

def test_grafana():
    """Test Grafana connectivity"""
    try:
        response = httpx.get('http://localhost:3000/api/health', timeout=5)
        if response.status_code == 200:
            print_status("Grafana is healthy", "OK")
            return True
        else:
            print_status(f"Grafana returned status {response.status_code}", "FAIL")
            return False
    except Exception as e:
        print_status(f"Grafana connection failed: {e}", "FAIL")
        return False

def test_api():
    """Test SAIMon API"""
    try:
        response = httpx.get('http://localhost:8000/api/v1/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status(f"SAIMon API is {data.get('status', 'unknown')}", "OK")
            return True
        else:
            print_status(f"API returned status {response.status_code}", "FAIL")
            return False
    except Exception as e:
        print_status(f"API connection failed: {e}", "FAIL")
        return False

def test_api_detailed():
    """Test SAIMon API with detailed health check"""
    try:
        response = httpx.get('http://localhost:8000/api/v1/health/detailed', timeout=10)
        if response.status_code == 200:
            data = response.json()
            deps = data.get('dependencies', {})
            
            for service, status in deps.items():
                if status == 'healthy':
                    print_status(f"API → {service}: {status}", "OK")
                else:
                    print_status(f"API → {service}: {status}", "WARN")
            
            return data.get('status') == 'healthy'
        else:
            print_status(f"Detailed health check failed", "FAIL")
            return False
    except Exception as e:
        print_status(f"Detailed health check error: {e}", "FAIL")
        return False

def test_prometheus_metrics():
    """Test Prometheus metrics availability"""
    try:
        from prometheus_api_client import PrometheusConnect
        prom = PrometheusConnect(url='http://localhost:9090', disable_ssl=True)
        
        # Test a simple query
        result = prom.custom_query(query='up')
        
        if result:
            print_status(f"Prometheus metrics available ({len(result)} targets)", "OK")
            return True
        else:
            print_status("No Prometheus metrics found", "WARN")
            return False
    except ImportError:
        print_status("prometheus-api-client not installed (pip install prometheus-api-client)", "WARN")
        return False
    except Exception as e:
        print_status(f"Prometheus query failed: {e}", "FAIL")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SAIMon Setup Verification")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    tests = [
        ("Prometheus Service", test_prometheus),
        ("Grafana Service", test_grafana),
        ("SAIMon API", test_api),
        ("API Detailed Health", test_api_detailed),
        ("Prometheus Metrics", test_prometheus_metrics),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTesting: {name}")
        print("-" * 40)
        results.append(test_func())
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print_status(f"All tests passed! ({passed}/{total})", "OK")
        print("\n✅ SAIMon is ready to use!")
        print("\nNext steps:")
        print("  1. Open Grafana: http://localhost:3000")
        print("  2. View API docs: http://localhost:8000/docs")
        print("  3. Check Prometheus: http://localhost:9090")
        sys.exit(0)
    else:
        print_status(f"Some tests failed ({passed}/{total} passed)", "FAIL")
        print("\n❌ Please check the error messages above")
        print("\nTroubleshooting:")
        print("  1. Run: docker-compose ps")
        print("  2. Check logs: docker-compose logs")
        print("  3. Restart: docker-compose restart")
        sys.exit(1)

if __name__ == "__main__":
    main()
