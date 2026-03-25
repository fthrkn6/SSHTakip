"""
Performance Load Testing Setup
Tools for load testing the application and identifying bottlenecks
Run with: pip install locust, then: locust -f load_test.py
"""

from locust import HttpUser, task, between, TaskSet
import random
import time

class DashboardLoadTest(TaskSet):
    """Load test dashboard endpoints"""
    
    def on_start(self):
        """Login before starting tests"""
        self.project_codes = ['belgrad', 'istanbul', 'ankara', 'izmir']
        self.user_id = 1
    
    @task(3)
    def dashboard_load(self):
        """Load main dashboard"""
        response = self.client.get('/dashboard')
        if response.status_code != 200:
            print(f"❌ Dashboard load failed: {response.status_code}")
    
    @task(2)
    def health_check(self):
        """Check system health"""
        response = self.client.get('/performance/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: DB={data.get('database', {}).get('status')}, "
                  f"Cache={data.get('cache', {}).get('status')}")
    
    @task(2)
    def get_reports_list(self):
        """Load reports list"""
        response = self.client.get('/api/reports/templates')
        if response.status_code != 200:
            print(f"❌ Reports list failed: {response.status_code}")
    
    @task(2)
    def get_kpi_metrics(self):
        """Load KPI metrics"""
        response = self.client.get('/performance/metrics')
        if response.status_code != 200:
            print(f"❌ KPI metrics failed: {response.status_code}")
    
    @task(1)
    def generate_report(self):
        """Generate sample report"""
        payload = {
            'template_name': 'daily_ops',
            'format': 'json',
            'filters': {
                'project_code': random.choice(self.project_codes),
                'date_range': 'today'
            }
        }
        response = self.client.post('/api/reports/generate', json=payload)
        if response.status_code != 200:
            print(f"⚠️  Report generation returned: {response.status_code}")


class EquipmentLoadTest(TaskSet):
    """Load test equipment endpoints"""
    
    def on_start(self):
        self.project_codes = ['belgrad', 'istanbul']
    
    @task(4)
    def list_equipment(self):
        """Get equipment list"""
        project = random.choice(self.project_codes)
        response = self.client.get(f'/equipment?project_code={project}')
        if response.status_code != 200:
            print(f"❌ Equipment list failed: {response.status_code}")
    
    @task(2)
    def get_equipment_detail(self):
        """Get single equipment"""
        # Assuming IDs 1-100 exist
        equipment_id = random.randint(1, 100)
        response = self.client.get(f'/equipment/{equipment_id}')
        if response.status_code != 200:
            print(f"⚠️  Equipment detail returned: {response.status_code}")
    
    @task(2)
    def filter_equipment(self):
        """Filter equipment by status"""
        statuses = ['çalışan', 'arızalı', 'bakımda']
        payload = {'status': random.choice(statuses)}
        response = self.client.get('/equipment/filter', params=payload)
        if response.status_code != 200:
            print(f"⚠️  Equipment filter returned: {response.status_code}")


class CacheLoadTest(TaskSet):
    """Load test cache operations"""
    
    def on_start(self):
        self.cache_keys = ['equipment:active', 'failures:recent', 'metrics:kpi']
    
    @task(5)
    def hit_cached_endpoint(self):
        """Test cached endpoints"""
        response = self.client.get('/performance/cache/stats')
        if response.status_code == 200:
            print(f"✅ Cache stats retrieved")
    
    @task(3)
    def clear_cache(self):
        """Clear cache (admin only)"""
        response = self.client.post('/performance/cache/clear')
        if response.status_code in [200, 403]:
            print(f"✅ Cache clear attempt returned: {response.status_code}")


class DashboardUser(HttpUser):
    """Simulates a dashboard user"""
    tasks = [DashboardLoadTest]
    wait_time = between(2, 5)


class EquipmentUser(HttpUser):
    """Simulates an equipment manager"""
    tasks = [EquipmentLoadTest]
    wait_time = between(3, 8)


class CacheMonitorUser(HttpUser):
    """Simulates admin monitoring cache"""
    tasks = [CacheLoadTest]
    wait_time = between(5, 10)


# Performance testing utilities
class PerformanceTestRunner:
    """Run performance tests and collect metrics"""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.results = {}
    
    def test_endpoint(self, endpoint, method='GET', payload=None, iterations=10):
        """
        Test endpoint performance
        
        Usage:
            runner = PerformanceTestRunner()
            results = runner.test_endpoint('/dashboard', iterations=100)
            print(f"Average response time: {results['avg_time']:.2f}s")
        """
        import requests
        
        times = []
        errors = 0
        
        print(f"\n🔍 Testing {method} {endpoint} ({iterations} iterations)...")
        
        for i in range(iterations):
            try:
                start = time.time()
                
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{endpoint}")
                elif method == 'POST':
                    response = requests.post(f"{self.base_url}{endpoint}", json=payload)
                
                elapsed = time.time() - start
                times.append(elapsed)
                
                if response.status_code != 200:
                    errors += 1
                
                # Print progress
                if (i + 1) % max(1, iterations // 10) == 0:
                    print(f"  Progress: {i + 1}/{iterations} ({len(times)} successful)")
                
            except Exception as e:
                print(f"  ❌ Request failed: {str(e)}")
                errors += 1
        
        # Calculate metrics
        if times:
            results = {
                'endpoint': endpoint,
                'method': method,
                'iterations': iterations,
                'successful': len(times),
                'errors': errors,
                'min_time': min(times),
                'max_time': max(times),
                'avg_time': sum(times) / len(times),
                'median_time': sorted(times)[len(times) // 2],
                'p95_time': sorted(times)[int(len(times) * 0.95)],
                'p99_time': sorted(times)[int(len(times) * 0.99)],
            }
        else:
            results = {'error': 'No successful requests'}
        
        self.results[endpoint] = results
        return results
    
    def test_concurrent_users(self, endpoint, num_users=10, duration=30):
        """
        Simulate concurrent users hitting endpoint
        
        Usage:
            runner.test_concurrent_users('/dashboard', num_users=100, duration=60)
        """
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def user_thread():
            import requests
            start_time = time.time()
            count = 0
            errors = 0
            total_time = 0
            
            while time.time() - start_time < duration:
                try:
                    req_start = time.time()
                    response = requests.get(f"{self.base_url}{endpoint}")
                    req_time = time.time() - req_start
                    
                    total_time += req_time
                    count += 1
                    
                    if response.status_code != 200:
                        errors += 1
                except Exception as e:
                    errors += 1
            
            results_queue.put({
                'requests': count,
                'errors': errors,
                'total_time': total_time,
                'avg_time': total_time / count if count > 0 else 0
            })
        
        print(f"\n⚡ Load testing {endpoint} with {num_users} concurrent users for {duration}s...")
        
        threads = []
        for i in range(num_users):
            t = threading.Thread(target=user_thread)
            t.start()
            threads.append(t)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Aggregate results
        aggregate = {
            'total_requests': 0,
            'total_errors': 0,
            'total_time': 0,
            'avg_time': 0
        }
        
        while not results_queue.empty():
            result = results_queue.get()
            aggregate['total_requests'] += result['requests']
            aggregate['total_errors'] += result['errors']
            aggregate['total_time'] += result['total_time']
        
        if aggregate['total_requests'] > 0:
            aggregate['avg_time'] = aggregate['total_time'] / aggregate['total_requests']
            aggregate['requests_per_sec'] = aggregate['total_requests'] / duration
        
        return aggregate
    
    def print_report(self):
        """Print performance test report"""
        print("\n" + "="*60)
        print("PERFORMANCE TEST REPORT")
        print("="*60 + "\n")
        
        for endpoint, results in self.results.items():
            if 'error' in results:
                print(f"❌ {endpoint}: {results['error']}")
                continue
            
            print(f"📊 {results['method']} {endpoint}")
            print(f"   Iterations: {results['iterations']}")
            print(f"   Successful: {results['successful']}/{results['iterations']}")
            print(f"   Errors: {results['errors']}")
            print(f"   Response Times:")
            print(f"     • Min: {results['min_time']*1000:.2f}ms")
            print(f"     • Avg: {results['avg_time']*1000:.2f}ms")
            print(f"     • p95: {results['p95_time']*1000:.2f}ms")
            print(f"     • p99: {results['p99_time']*1000:.2f}ms")
            print(f"     • Max: {results['max_time']*1000:.2f}ms")
            print()
        
        print("="*60)
        print("✅ Test completed!\n")


# CLI for running tests
if __name__ == '__main__':
    print("""
    Load Testing Setup
    
    Option 1: Locust GUI (recommended)
        pip install locust
        locust -f load_test.py
        Then open http://localhost:8089
    
    Option 2: Command line tests
        python load_test.py --test-endpoints
    
    Option 3: Performance benchmarking
        python load_test.py --benchmark
    """)
    
    import sys
    
    if '--benchmark' in sys.argv:
        runner = PerformanceTestRunner()
        
        # Test individual endpoints
        runner.test_endpoint('/dashboard', iterations=50)
        runner.test_endpoint('/performance/health', iterations=100)
        runner.test_endpoint('/api/reports/templates', iterations=50)
        
        # Test concurrent load
        concurrent_results = runner.test_concurrent_users(
            '/dashboard',
            num_users=20,
            duration=10
        )
        print(f"\nConcurrent load results:")
        print(f"  Total requests: {concurrent_results['total_requests']}")
        print(f"  Requests/sec: {concurrent_results['requests_per_sec']:.2f}")
        print(f"  Avg response: {concurrent_results['avg_time']*1000:.2f}ms\n")
        
        runner.print_report()
