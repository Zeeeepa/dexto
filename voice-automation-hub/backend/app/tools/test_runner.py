"""Test runner tools for executing pytest and collecting results."""

from typing import Dict, Any, List, Optional
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class TestRunner:
    """Tools for running tests and collecting results."""

    def __init__(self):
        """Initialize test runner."""
        self.test_history: List[Dict[str, Any]] = []
        self.max_history = 100

    def run_pytest(
        self,
        test_path: str,
        markers: Optional[List[str]] = None,
        verbose: bool = True,
        coverage: bool = False,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Run pytest tests.

        Args:
            test_path: Path to tests (file or directory)
            markers: Optional pytest markers to filter tests
            verbose: Verbose output
            coverage: Enable coverage reporting
            timeout: Timeout in seconds

        Returns:
            Test results
        """
        start_time = datetime.now()

        # Build pytest command
        cmd = ["pytest", test_path]

        if verbose:
            cmd.append("-v")

        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])

        if coverage:
            cmd.extend(["--cov", "--cov-report=json"])

        # Add JSON output for parsing
        cmd.extend(["--json-report", "--json-report-file=/tmp/pytest_report.json"])

        try:
            # Run pytest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            # Parse JSON report
            test_results = self._parse_json_report("/tmp/pytest_report.json")

            # Parse coverage if enabled
            coverage_data = None
            if coverage:
                coverage_data = self._parse_coverage_report()

            duration = (datetime.now() - start_time).total_seconds()

            final_result = {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "test_path": test_path,
                "markers": markers,
                "test_results": test_results,
                "coverage": coverage_data,
                "stdout": result.stdout[-1000:],  # Last 1000 chars
                "stderr": result.stderr[-1000:] if result.stderr else "",
                "duration": duration,
                "timestamp": start_time.isoformat(),
            }

            # Store in history
            self._add_to_history(final_result)

            logger.info(
                f"Tests completed: {test_path} "
                f"(passed: {test_results.get('passed', 0)}, "
                f"failed: {test_results.get('failed', 0)}, "
                f"duration: {duration:.2f}s)"
            )

            return final_result

        except subprocess.TimeoutExpired:
            logger.error(f"Test timeout: {test_path}")
            return {
                "success": False,
                "error": f"Tests timed out after {timeout}s",
                "test_path": test_path,
            }
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_path": test_path,
            }

    def run_tests_by_pattern(
        self,
        directory: str,
        pattern: str = "test_*.py",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run tests matching pattern.

        Args:
            directory: Test directory
            pattern: File pattern
            **kwargs: Additional pytest arguments

        Returns:
            Test results
        """
        # Find matching test files
        test_dir = Path(directory)
        test_files = list(test_dir.glob(f"**/{pattern}"))

        if not test_files:
            return {
                "success": False,
                "error": f"No test files found matching {pattern} in {directory}",
            }

        logger.info(f"Found {len(test_files)} test files")

        # Run tests on directory
        return self.run_pytest(directory, **kwargs)

    def run_specific_tests(
        self,
        test_cases: List[str],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run specific test cases.

        Args:
            test_cases: List of test identifiers (e.g., 'test_file.py::test_function')
            **kwargs: Additional pytest arguments

        Returns:
            Test results
        """
        # Run tests for each case
        cmd = ["pytest"] + test_cases

        if kwargs.get("verbose", True):
            cmd.append("-v")

        cmd.extend(["--json-report", "--json-report-file=/tmp/pytest_report.json"])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=kwargs.get("timeout", 300),
            )

            test_results = self._parse_json_report("/tmp/pytest_report.json")

            return {
                "success": result.returncode == 0,
                "test_cases": test_cases,
                "test_results": test_results,
                "stdout": result.stdout[-1000:],
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_coverage_report(self) -> Dict[str, Any]:
        """Get latest coverage report."""
        return self._parse_coverage_report()

    def _parse_json_report(self, report_path: str) -> Dict[str, Any]:
        """Parse pytest JSON report."""
        try:
            with open(report_path, "r") as f:
                data = json.load(f)

            summary = data.get("summary", {})

            return {
                "total": summary.get("total", 0),
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
                "skipped": summary.get("skipped", 0),
                "errors": summary.get("error", 0),
                "duration": data.get("duration", 0),
                "tests": self._extract_test_details(data.get("tests", [])),
            }

        except Exception as e:
            logger.warning(f"Failed to parse JSON report: {e}")
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
            }

    def _extract_test_details(self, tests: List[Dict]) -> List[Dict[str, Any]]:
        """Extract test details from report."""
        details = []

        for test in tests[:20]:  # Limit to first 20 tests
            details.append({
                "name": test.get("nodeid", ""),
                "outcome": test.get("outcome", ""),
                "duration": test.get("duration", 0),
                "error": test.get("call", {}).get("longrepr", "") if test.get("outcome") == "failed" else None,
            })

        return details

    def _parse_coverage_report(self) -> Optional[Dict[str, Any]]:
        """Parse coverage JSON report."""
        try:
            with open("coverage.json", "r") as f:
                data = json.load(f)

            totals = data.get("totals", {})

            return {
                "percent_covered": totals.get("percent_covered", 0),
                "num_statements": totals.get("num_statements", 0),
                "missing_lines": totals.get("missing_lines", 0),
                "covered_lines": totals.get("covered_lines", 0),
                "files": len(data.get("files", {})),
            }

        except Exception as e:
            logger.warning(f"Failed to parse coverage report: {e}")
            return None

    def validate_test_results(
        self,
        results: Dict[str, Any],
        min_pass_rate: float = 1.0,
        max_duration: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Validate test results against criteria.

        Args:
            results: Test results
            min_pass_rate: Minimum pass rate (0-1)
            max_duration: Maximum duration in seconds

        Returns:
            Validation result
        """
        test_results = results.get("test_results", {})
        total = test_results.get("total", 0)
        passed = test_results.get("passed", 0)

        if total == 0:
            return {
                "valid": False,
                "reason": "No tests executed",
            }

        pass_rate = passed / total if total > 0 else 0

        checks = {
            "pass_rate": {
                "passed": pass_rate >= min_pass_rate,
                "value": pass_rate,
                "threshold": min_pass_rate,
            }
        }

        if max_duration:
            duration = results.get("duration", 0)
            checks["duration"] = {
                "passed": duration <= max_duration,
                "value": duration,
                "threshold": max_duration,
            }

        all_passed = all(check["passed"] for check in checks.values())

        return {
            "valid": all_passed,
            "checks": checks,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": test_results.get("failed", 0),
                "pass_rate": pass_rate,
            },
        }

    def get_test_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get test execution history."""
        return self.test_history[-limit:]

    def clear_history(self):
        """Clear test history."""
        self.test_history.clear()

    def _add_to_history(self, result: Dict[str, Any]):
        """Add result to history."""
        self.test_history.append(result)

        # Limit history size
        if len(self.test_history) > self.max_history:
            self.test_history = self.test_history[-self.max_history:]


# Global test runner instance
test_runner = TestRunner()


# MCP tool definitions
def run_tests(test_path: str, **kwargs) -> Dict[str, Any]:
    """Run pytest tests via MCP."""
    return test_runner.run_pytest(test_path, **kwargs)


def run_tests_with_coverage(test_path: str, **kwargs) -> Dict[str, Any]:
    """Run tests with coverage via MCP."""
    return test_runner.run_pytest(test_path, coverage=True, **kwargs)


def get_coverage() -> Dict[str, Any]:
    """Get coverage report via MCP."""
    return test_runner.get_coverage_report()


def validate_tests(results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Validate test results via MCP."""
    return test_runner.validate_test_results(results, **kwargs)

