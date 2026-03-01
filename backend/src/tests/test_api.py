"""
Test suite for Image Search API
Tests filters: speciality, disease_area
"""
import requests
import json
from typing import Dict, Any


class APITester:
    """Class to handle all API tests"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.results = []
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        print("\n" + "=" * 60)
        print("TEST 1: Health Check")
        print("=" * 60)
        try:
            response = requests.get(f"{self.base_url}/health-check", timeout=5)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def test_search_all_images(self) -> bool:
        """Test getting all images without filters"""
        print("\n" + "=" * 60)
        print("TEST 2: Get All Images (no filters)")
        print("=" * 60)
        try:
            response = requests.get(f"{self.base_url}/images/search", timeout=5)
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Total images: {data['total']}")
            if data['results']:
                print(f"First image: {json.dumps(data['results'][0], indent=2)}")
            return response.status_code == 200 and data['total'] > 0
        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def test_filter_oncologist_all(self) -> bool:
        """Test filtering by oncologist speciality"""
        print("\n" + "=" * 60)
        print("TEST 3: Filter speciality=oncologist, disease_area=all")
        print("=" * 60)
        try:
            response = requests.get(
                f"{self.base_url}/images/search", 
                params={"speciality": "oncologist", "disease_area": "all"},
                timeout=5
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Total results: {data['total']}")
            return response.status_code == 200 and data['total'] > 0
        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def test_filter_disease_cancer_all_speciality(self) -> bool:
        """Test filtering by cancer disease area"""
        print("\n" + "=" * 60)
        print("TEST 4: Filter speciality=all, disease_area=cancer")
        print("=" * 60)
        try:
            response = requests.get(
                f"{self.base_url}/images/search", 
                params={"speciality": "all", "disease_area": "cancer"},
                timeout=5
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Total results: {data['total']}")
            return response.status_code == 200 and data['total'] > 0
        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def test_filter_pediatrician_child_health(self) -> bool:
        """Test filtering by pediatrician and child health"""
        print("\n" + "=" * 60)
        print("TEST 5: Filter speciality=pediatrician, disease_area=child health")
        print("=" * 60)
        try:
            response = requests.get(
                f"{self.base_url}/images/search", 
                params={"speciality": "pediatrician", "disease_area": "child health"},
                timeout=5
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Total results: {data['total']}")
            return response.status_code == 200 and data['total'] > 0
        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def test_case_insensitive_speciality(self) -> bool:
        """Test case insensitive search"""
        print("\n" + "=" * 60)
        print("TEST 6: Case Insensitive speciality (ONCOLOGIST vs oncologist)")
        print("=" * 60)
        try:
            resp1 = requests.get(
                f"{self.base_url}/images/search", 
                params={"speciality": "ONCOLOGIST"},
                timeout=5
            )
            resp2 = requests.get(
                f"{self.base_url}/images/search", 
                params={"speciality": "oncologist"},
                timeout=5
            )
            data1 = resp1.json()
            data2 = resp2.json()
            print(f"Uppercase results: {data1['total']}")
            print(f"Lowercase results: {data2['total']}")
            return data1['total'] == data2['total'] and data1['total'] > 0
        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def test_filter_general_physician_infectious(self) -> bool:
        """Test filtering by general physician and infectious diseases"""
        print("\n" + "=" * 60)
        print("TEST 7: Filter speciality=general physician, disease_area=infectious diseases")
        print("=" * 60)
        try:
            response = requests.get(
                f"{self.base_url}/images/search", 
                params={"speciality": "general physician", "disease_area": "infectious diseases"},
                timeout=5
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Total results: {data['total']}")
            return response.status_code == 200 and data['total'] >= 0
        except Exception as e:
            print(f"ERROR: {e}")
            return False



    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("\n" + "#" * 60)
        print("# IMAGE SEARCH API TEST SUITE")
        print("#" * 60)

        tests = [
            self.test_health_check,
            self.test_search_all_images,
            self.test_filter_oncologist_all,
            self.test_filter_disease_cancer_all_speciality,
            self.test_filter_pediatrician_child_health,
            self.test_case_insensitive_speciality,
            self.test_filter_general_physician_infectious,
        ]

        results = []
        for test in tests:
            try:
                passed = test()
                results.append(("✓ PASS" if passed else "✗ FAIL", test.__name__))
            except Exception as e:
                print(f"ERROR: {e}")
                results.append(("✗ ERROR", test.__name__))

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        for status, name in results:
            print(f"{status}: {name}")

        passed_count = sum(1 for status, _ in results if "PASS" in status)
        print(f"\nPassed: {passed_count}/{len(tests)}")
        
        return {
            "total": len(tests),
            "passed": passed_count,
            "failed": len(tests) - passed_count,
            "results": results
        }
