"""
Test runner module for automated API testing on startup
"""
import asyncio
import threading
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_api import APITester


class TestRunner:
    
    def __init__(self):
        self.tester = APITester()
        self.results = None
    
    def run(self) -> Dict[str, Any]:
        try:
            import io
            from contextlib import redirect_stdout
            
            with redirect_stdout(io.StringIO()):
                self.results = self.tester.run_all_tests()
            return self.results
        except Exception as e:
            print(f"Error running tests: {e}")
            return {"error": str(e)}
    
    def start(self):
        thread = threading.Thread(target=self._run_in_background, daemon=True)
        thread.start()
    
    def _run_in_background(self):
        try:
            self.run()
        except Exception as e:
            print(f"Background test execution error: {e}")


test_runner = TestRunner()
