#!/usr/bin/env python
"""
Load Testing Script for HealthKart360 Application
Tests concurrent user capacity and response times
"""

import asyncio
import aiohttp
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import threading
import requests
from datetime import datetime

class LoadTester:
    def __init__(self, base_url="http://localhost:8000", max_workers=10):
        self.base_url = base_url.rstrip('/')
        self.max_workers = max_workers
        self.results = []
        self.errors = []

    async def make_request_async(self, session, url, request_id):
        """Make an async HTTP request"""
        start_time = time.time()
        try:
            async with session.get(url) as response:
                content = await response.text()
                response_time = time.time() - start_time
                return {
                    'request_id': request_id,
                    'status_code': response.status,
                    'response_time': response_time,
                    'success': response.status == 200
                }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                'request_id': request_id,
                'status_code': None,
                'response_time': response_time,
                'success': False,
                'error': str(e)
            }

    async def run_async_load_test(self, num_requests=100, concurrent_users=10):
        """Run async load test"""
        print(f"Starting async load test: {num_requests} requests, {concurrent_users} concurrent users")

        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(num_requests):
                url = f"{self.base_url}/"
                task = self.make_request_async(session, url, i)
                tasks.append(task)

            # Execute in batches to simulate concurrent users
            results = []
            for i in range(0, len(tasks), concurrent_users):
                batch = tasks[i:i + concurrent_users]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                results.extend(batch_results)
                await asyncio.sleep(0.1)  # Small delay between batches

        return results

    def run_sync_load_test(self, num_requests=100, concurrent_users=10):
        """Run synchronous load test with threading"""
        print(f"Starting sync load test: {num_requests} requests, {concurrent_users} concurrent users")

        def make_request(request_id):
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}/", timeout=30)
                response_time = time.time() - start_time
                return {
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                response_time = time.time() - start_time
                return {
                    'request_id': request_id,
                    'status_code': None,
                    'response_time': response_time,
                    'success': False,
                    'error': str(e)
                }

        results = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            for future in futures:
                results.append(future.result())

        return results

    def analyze_results(self, results):
        """Analyze test results"""
        successful_requests = [r for r in results if r.get('success', False)]
        failed_requests = [r for r in results if not r.get('success', False)]

        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            analysis = {
                'total_requests': len(results),
                'successful_requests': len(successful_requests),
                'failed_requests': len(failed_requests),
                'success_rate': (len(successful_requests) / len(results)) * 100,
                'avg_response_time': statistics.mean(response_times),
                'median_response_time': statistics.median(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                '95th_percentile': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
                'requests_per_second': len(results) / sum(r['response_time'] for r in results)
            }
        else:
            analysis = {
                'total_requests': len(results),
                'successful_requests': 0,
                'failed_requests': len(failed_requests),
                'success_rate': 0,
                'error': 'No successful requests'
            }

        return analysis

    def print_report(self, analysis):
        """Print test report"""
        print("\n" + "="*60)
        print("LOAD TEST REPORT")
        print("="*60)
        print(f"Total Requests: {analysis['total_requests']}")
        print(f"Successful Requests: {analysis['successful_requests']}")
        print(f"Failed Requests: {analysis['failed_requests']}")

        if 'avg_response_time' in analysis:
            print("\nResponse Time Statistics:")
            print(f"Average: {analysis['avg_response_time']:.3f} seconds")
            print(f"Median: {analysis['median_response_time']:.3f} seconds")
            print(f"Min: {analysis['min_response_time']:.3f} seconds")
            print(f"Max: {analysis['max_response_time']:.3f} seconds")
            print(f"95th Percentile: {analysis['95th_percentile']:.3f} seconds")
            print(f"Requests per Second: {analysis['requests_per_second']:.1f}")

        print("="*60)

def main():
    # Test different concurrency levels
    tester = LoadTester(base_url="http://localhost:8000")

    test_scenarios = [
        (50, 5),    # 50 requests, 5 concurrent
        (100, 10),  # 100 requests, 10 concurrent
        (200, 20),  # 200 requests, 20 concurrent
        (500, 25),  # 500 requests, 25 concurrent
    ]

    print("HealthKart360 Load Testing")
    print("Testing concurrent user capacity...")
    print(f"Base URL: {tester.base_url}")
    print(f"Test started at: {datetime.now()}")

    for num_requests, concurrent_users in test_scenarios:
        print(f"\n--- Testing {concurrent_users} concurrent users ---")

        try:
            # Run async test
            results = asyncio.run(tester.run_async_load_test(num_requests, concurrent_users))
            analysis = tester.analyze_results(results)
            tester.print_report(analysis)

            # Check if success rate is acceptable (>95%)
            if analysis['success_rate'] < 95:
                print(f"⚠️  WARNING: Low success rate ({analysis['success_rate']:.1f}%) at {concurrent_users} concurrent users")
                break

            # Check response time (<2 seconds average)
            if 'avg_response_time' in analysis and analysis['avg_response_time'] > 2.0:
                print(f"⚠️  WARNING: High response time ({analysis['avg_response_time']:.2f}s) at {concurrent_users} concurrent users")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            break

if __name__ == "__main__":
    main()
