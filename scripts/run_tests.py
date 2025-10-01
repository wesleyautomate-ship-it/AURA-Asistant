import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

#!/usr/bin/env python3
"""
Comprehensive Test Runner for Dubai Real Estate RAG Chat System
Provides unified interface for running all types of tests with various options
"""

import os
import sys
import argparse
import subprocess
import time
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestRunner:
    """Comprehensive test runner with multiple test types and configurations."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        self.reports_dir = project_root / "test_reports"
        self.logs_dir = project_root / "logs"
        
        # Ensure directories exist
        self.reports_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Test configurations
        self.test_configs = {
            "unit": {
                "path": "tests/unit",
                "markers": "unit",
                "timeout": 300,
                "parallel": True
            },
            "integration": {
                "path": "tests/integration", 
                "markers": "integration",
                "timeout": 600,
                "parallel": False
            },
            "performance": {
                "path": "tests/performance",
                "markers": "performance",
                "timeout": 1800,
                "parallel": False
            },
            "security": {
                "path": "tests/security",
                "markers": "security", 
                "timeout": 900,
                "parallel": False
            },
            "e2e": {
                "path": "tests/e2e",
                "markers": "e2e",
                "timeout": 1200,
                "parallel": False
            },
            "load": {
                "path": "tests/load",
                "markers": "load",
                "timeout": 3600,
                "parallel": False
            }
        }
        
        # Performance test scenarios
        self.performance_scenarios = {
            "smoke": {"users": 5, "duration": 60, "ramp_up": 10},
            "load": {"users": 20, "duration": 300, "ramp_up": 60},
            "stress": {"users": 50, "duration": 600, "ramp_up": 120},
            "spike": {"users": 100, "duration": 300, "ramp_up": 30}
        }

    def setup_logging(self):
        """Setup logging configuration."""
        log_file = self.logs_dir / f"test_runner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)

    def run_command(self, command: List[str], timeout: int = None) -> Dict[str, Any]:
        """Run a command and return results."""
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        try:
            self.logger.info(f"Running command: {' '.join(command)}")
            
            start_time = time.time()
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
                env=env
            )
            end_time = time.time()
            
            if result.returncode != 0:
                self.logger.error(f"Command failed with exit code {result.returncode}")
                self.logger.error(f"Stdout: {result.stdout}")
                self.logger.error(f"Stderr: {result.stderr}")
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": end_time - start_time
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out after {timeout} seconds")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "duration": timeout
            }
        except Exception as e:
            self.logger.error(f"Error running command: {e}")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": 0
            }

    def setup_test_environment(self) -> bool:
        """Setup test environment (database, services, etc.)."""
        self.logger.info("Setting up test environment...")
        
        # Install test dependencies
        test_requirements = self.project_root / "tests" / "requirements-test.txt"
        if test_requirements.exists():
            result = self.run_command([
                sys.executable, "-m", "pip", "install", "-r", str(test_requirements)
            ])
            if not result["success"]:
                self.logger.error("Failed to install test dependencies")
                return False
        
        # Setup test database
        result = self.run_command([
            sys.executable, "scripts/create_test_db.py"
        ])
        
        if not result["success"]:
            self.logger.error("Failed to setup test database")
            return False
        
        self.logger.info("Test environment setup completed")
        return True

    def cleanup_test_environment(self):
        """Cleanup test environment."""
        self.logger.info("Cleaning up test environment...")
        
        # Remove test database
        test_db = self.project_root / "test.db"
        if test_db.exists():
            test_db.unlink()
        
        # Remove test ChromaDB directory
        test_chroma = self.project_root / "test_chroma"
        if test_chroma.exists():
            shutil.rmtree(test_chroma)
        
        # Remove test uploads
        test_uploads = self.project_root / "test_uploads"
        if test_uploads.exists():
            shutil.rmtree(test_uploads)
        
        self.logger.info("Test environment cleanup completed")

    def run_pytest_tests(self, test_type: str, markers: str = None, 
                        parallel: bool = False, timeout: int = None) -> Dict[str, Any]:
        """Run pytest tests with specified configuration."""
        config = self.test_configs.get(test_type, {})
        
        command = [
            sys.executable, "-m", "pytest",
            config.get("path", f"tests/{test_type}"),
            "-v",
            "--tb=short",
            "--strict-markers",
            f"--html={self.reports_dir}/{test_type}_report.html",
            "--self-contained-html",
            f"--junitxml={self.reports_dir}/{test_type}_junit.xml",
            f"--cov=backend",
            f"--cov-report=html:{self.reports_dir}/{test_type}_coverage",
            f"--cov-report=xml:{self.reports_dir}/{test_type}_coverage.xml",
            "--cov-report=term-missing"
        ]
        
        if markers:
            command.extend(["-m", markers])
        
        if parallel:
            command.extend(["-n", "auto"])
        
        if timeout:
            command.extend(["--timeout", str(timeout)])
        
        return self.run_command(command, timeout=timeout)

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests."""
        self.logger.info("Running unit tests...")
        return self.run_pytest_tests("unit")

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        self.logger.info("Running integration tests...")
        return self.run_pytest_tests("integration")

    def run_performance_tests(self, scenario: str = "load") -> Dict[str, Any]:
        """Run performance tests with specified scenario."""
        self.logger.info(f"Running performance tests with scenario: {scenario}")
        
        if scenario not in self.performance_scenarios:
            self.logger.error(f"Unknown performance scenario: {scenario}")
            return {"success": False, "error": f"Unknown scenario: {scenario}"}
        
        # Set environment variables for performance test
        env = os.environ.copy()
        scenario_config = self.performance_scenarios[scenario]
        env.update({
            "PERFORMANCE_TEST_USERS": str(scenario_config["users"]),
            "PERFORMANCE_TEST_DURATION": str(scenario_config["duration"]),
            "PERFORMANCE_TEST_RAMP_UP": str(scenario_config["ramp_up"])
        })
        
        return self.run_pytest_tests("performance", timeout=1800)

    def run_security_tests(self) -> Dict[str, Any]:
        """Run security tests."""
        self.logger.info("Running security tests...")
        return self.run_pytest_tests("security")

    def run_load_tests(self, users: int = 20, duration: int = 300) -> Dict[str, Any]:
        """Run load tests using Locust."""
        self.logger.info(f"Running load tests with {users} users for {duration} seconds...")
        
        # Create Locust configuration
        locust_config = {
            "users": users,
            "spawn_rate": max(1, users // 10),
            "run_time": f"{duration}s",
            "host": "http://localhost:8000"
        }
        
        # Run Locust
        command = [
            sys.executable, "-m", "locust",
            "--headless",
            "--users", str(locust_config["users"]),
            "--spawn-rate", str(locust_config["spawn_rate"]),
            "--run-time", locust_config["run_time"],
            "--host", locust_config["host"],
            "--html", str(self.reports_dir / "load_test_report.html"),
            "--csv", str(self.reports_dir / "load_test_results")
        ]
        
        return self.run_command(command, timeout=duration + 60)

    def run_code_quality_checks(self) -> Dict[str, Any]:
        """Run code quality checks."""
        self.logger.info("Running code quality checks...")
        
        results = {}
        
        # Black formatting check
        results["black"] = self.run_command([
            sys.executable, "-m", "black", "--check", "backend", "tests"
        ])
        
        # Flake8 linting
        results["flake8"] = self.run_command([
            sys.executable, "-m", "flake8", "backend", "tests"
        ])
        
        # MyPy type checking
        results["mypy"] = self.run_command([
            sys.executable, "-m", "mypy", "backend"
        ])
        
        # Bandit security analysis
        results["bandit"] = self.run_command([
            sys.executable, "-m", "bandit", "-r", "backend"
        ])
        
        # Safety dependency check
        results["safety"] = self.run_command([
            sys.executable, "-m", "safety", "check"
        ])
        
        return results

    def run_frontend_tests(self) -> Dict[str, Any]:
        """Run frontend tests."""
        self.logger.info("Running frontend tests...")
        
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            return {"success": False, "error": "Frontend directory not found"}
        
        # Install frontend dependencies
        result = self.run_command(["npm", "install"], cwd=frontend_dir)
        if not result["success"]:
            return result
        
        # Run frontend tests
        return self.run_command(["npm", "test"], cwd=frontend_dir)

    def run_docker_tests(self) -> Dict[str, Any]:
        """Run Docker build and test."""
        self.logger.info("Running Docker tests...")
        
        # Build Docker image
        build_result = self.run_command([
            "docker", "build", "-t", "dubai-estate-rag:test", "."
        ])
        
        if not build_result["success"]:
            return build_result
        
        # Run Docker container tests
        run_result = self.run_command([
            "docker", "run", "--rm", "-d", "--name", "test-container",
            "-p", "8000:8000", "dubai-estate-rag:test"
        ])
        
        if not run_result["success"]:
            return run_result
        
        # Wait for container to start
        time.sleep(10)
        
        # Test container health
        health_result = self.run_command([
            "curl", "-f", "http://localhost:8000/health"
        ])
        
        # Stop container
        self.run_command(["docker", "stop", "test-container"])
        
        return health_result

    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive test report."""
        report_file = self.reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(results),
                "passed": sum(1 for r in results.values() if r.get("success", False)),
                "failed": sum(1 for r in results.values() if not r.get("success", False))
            },
            "results": results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)

    def run_all_tests(self, test_types: List[str] = None, 
                     performance_scenario: str = "load",
                     load_users: int = 20) -> Dict[str, Any]:
        """Run all specified test types."""
        if test_types is None:
            test_types = ["unit", "integration", "performance", "security"]
        
        self.logger.info(f"Running all tests: {test_types}")
        
        # Setup environment
        if not self.setup_test_environment():
            return {"success": False, "error": "Failed to setup test environment", "results": {}}
        
        results = {}
        
        try:
            # Run code quality checks first
            results["code_quality"] = self.run_code_quality_checks()
            
            # Run specified test types
            for test_type in test_types:
                if test_type == "unit":
                    results["unit"] = self.run_unit_tests()
                elif test_type == "integration":
                    results["integration"] = self.run_integration_tests()
                elif test_type == "performance":
                    results["performance"] = self.run_performance_tests(performance_scenario)
                elif test_type == "security":
                    results["security"] = self.run_security_tests()
                elif test_type == "load":
                    results["load"] = self.run_load_tests(load_users)
                elif test_type == "frontend":
                    results["frontend"] = self.run_frontend_tests()
                elif test_type == "docker":
                    results["docker"] = self.run_docker_tests()
            
            # Generate report
            report_file = self.generate_test_report(results)
            self.logger.info(f"Test report generated: {report_file}")
            
            return {
                "success": all(r.get("success", False) for r in results.values()),
                "results": results,
                "report_file": report_file
            }
            
        finally:
            self.cleanup_test_environment()

def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Comprehensive Test Runner")
    
    parser.add_argument(
        "--test-types", 
        nargs="+",
        choices=["unit", "integration", "performance", "security", "load", "frontend", "docker", "all"],
        default=["unit", "integration"],
        help="Types of tests to run"
    )
    
    parser.add_argument(
        "--performance-scenario",
        choices=["smoke", "load", "stress", "spike"],
        default="load",
        help="Performance test scenario"
    )
    
    parser.add_argument(
        "--load-users",
        type=int,
        default=20,
        help="Number of users for load testing"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel where possible"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Test timeout in seconds"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize test runner
    runner = TestRunner(project_root)
    
    # Determine test types
    test_types = args.test_types
    if "all" in test_types:
        test_types = ["unit", "integration", "performance", "security", "load", "frontend", "docker"]
    
    # Run tests
    result = runner.run_all_tests(
        test_types=test_types,
        performance_scenario=args.performance_scenario,
        load_users=args.load_users
    )
    
    # Print summary
    if result["success"]:
        print("All tests passed!")
    else:
        print("Some tests failed!")
        for test_type, test_result in result["results"].items():
            if not test_result.get("success", False):
                print(f"  {test_type}: {test_result.get('error', 'Failed')}")
    
    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()
