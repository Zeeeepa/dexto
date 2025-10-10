"""CLI automation tools for executing shell commands, system operations, and process management."""

import subprocess
import os
import shlex
import platform
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CLITools:
    """Tools for CLI automation and system command execution."""

    def __init__(self):
        """Initialize CLI tools."""
        self.system = platform.system()
        self.shell = self._get_default_shell()
        self.command_history: List[Dict[str, Any]] = []
        self.max_history = 1000

    def _get_default_shell(self) -> str:
        """Get default shell for the system."""
        if self.system == "Windows":
            return "powershell.exe"
        return os.environ.get("SHELL", "/bin/bash")

    def execute_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        capture_output: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute shell command.

        Args:
            command: Command to execute
            cwd: Working directory
            env: Environment variables
            timeout: Timeout in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            Execution result with stdout, stderr, return code
        """
        try:
            start_time = datetime.now()
            
            # Prepare environment
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)

            # Execute command
            if self.system == "Windows":
                # Use PowerShell on Windows
                process = subprocess.run(
                    ["powershell.exe", "-Command", command],
                    cwd=cwd,
                    env=exec_env,
                    capture_output=capture_output,
                    text=True,
                    timeout=timeout,
                )
            else:
                # Use shell on Unix-like systems
                process = subprocess.run(
                    command,
                    cwd=cwd,
                    env=exec_env,
                    capture_output=capture_output,
                    text=True,
                    shell=True,
                    timeout=timeout,
                )

            duration = (datetime.now() - start_time).total_seconds()

            result = {
                "success": process.returncode == 0,
                "stdout": process.stdout if capture_output else None,
                "stderr": process.stderr if capture_output else None,
                "return_code": process.returncode,
                "duration": duration,
                "command": command,
                "cwd": cwd,
                "timestamp": start_time.isoformat(),
            }

            # Store in history
            self._add_to_history(result)

            logger.info(
                f"Command executed: {command[:50]}... "
                f"(code: {process.returncode}, duration: {duration:.2f}s)"
            )

            return result

        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {command}")
            return {
                "success": False,
                "error": "Command timed out",
                "timeout": timeout,
                "command": command,
            }
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command,
            }

    def execute_script(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        interpreter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute script file.

        Args:
            script_path: Path to script
            args: Script arguments
            interpreter: Script interpreter (e.g., 'python', 'node')

        Returns:
            Execution result
        """
        if not os.path.exists(script_path):
            return {
                "success": False,
                "error": f"Script not found: {script_path}",
            }

        # Determine interpreter
        if not interpreter:
            ext = os.path.splitext(script_path)[1].lower()
            interpreter_map = {
                ".py": "python",
                ".js": "node",
                ".sh": "bash",
                ".ps1": "powershell.exe",
                ".rb": "ruby",
            }
            interpreter = interpreter_map.get(ext, "")

        # Build command
        command_parts = []
        if interpreter:
            command_parts.append(interpreter)
        command_parts.append(script_path)
        if args:
            command_parts.extend(args)

        command = " ".join(shlex.quote(p) for p in command_parts)

        return self.execute_command(command)

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "system": platform.system(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage("/").total,
                "used": psutil.disk_usage("/").used,
                "free": psutil.disk_usage("/").free,
                "percent": psutil.disk_usage("/").percent,
            },
        }

    def list_processes(
        self, filter_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List running processes.

        Args:
            filter_name: Filter by process name

        Returns:
            List of process information
        """
        processes = []

        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = proc.info
                
                if filter_name and filter_name.lower() not in info["name"].lower():
                    continue

                processes.append({
                    "pid": info["pid"],
                    "name": info["name"],
                    "cpu_percent": info.get("cpu_percent", 0),
                    "memory_percent": info.get("memory_percent", 0),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

    def kill_process(self, pid: int, force: bool = False) -> Dict[str, Any]:
        """
        Kill process by PID.

        Args:
            pid: Process ID
            force: Whether to force kill

        Returns:
            Result of operation
        """
        try:
            process = psutil.Process(pid)
            process_name = process.name()

            if force:
                process.kill()
            else:
                process.terminate()

            logger.info(f"Process killed: {process_name} (PID: {pid})")

            return {
                "success": True,
                "pid": pid,
                "name": process_name,
                "forced": force,
            }

        except psutil.NoSuchProcess:
            return {
                "success": False,
                "error": f"Process not found: PID {pid}",
            }
        except psutil.AccessDenied:
            return {
                "success": False,
                "error": f"Access denied to kill process: PID {pid}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def set_environment_variable(
        self, name: str, value: str, permanent: bool = False
    ) -> Dict[str, Any]:
        """
        Set environment variable.

        Args:
            name: Variable name
            value: Variable value
            permanent: Whether to set permanently (system-wide)

        Returns:
            Result of operation
        """
        try:
            # Set for current process
            os.environ[name] = value

            if permanent:
                if self.system == "Windows":
                    # Set permanently on Windows
                    command = f'[Environment]::SetEnvironmentVariable("{name}", "{value}", "User")'
                    result = self.execute_command(command)
                    if not result["success"]:
                        return result
                else:
                    # On Unix, add to shell profile
                    profile_path = os.path.expanduser("~/.bashrc")
                    with open(profile_path, "a") as f:
                        f.write(f'\nexport {name}="{value}"\n')

            return {
                "success": True,
                "name": name,
                "value": value,
                "permanent": permanent,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_environment_variable(self, name: str) -> Optional[str]:
        """Get environment variable value."""
        return os.environ.get(name)

    def list_environment_variables(
        self, filter_prefix: Optional[str] = None
    ) -> Dict[str, str]:
        """
        List environment variables.

        Args:
            filter_prefix: Filter by prefix

        Returns:
            Dictionary of environment variables
        """
        env_vars = dict(os.environ)

        if filter_prefix:
            env_vars = {
                k: v for k, v in env_vars.items()
                if k.startswith(filter_prefix)
            }

        return env_vars

    def get_command_history(
        self, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get command execution history."""
        return self.command_history[-limit:]

    def clear_command_history(self):
        """Clear command history."""
        self.command_history.clear()
        logger.info("Command history cleared")

    def _add_to_history(self, result: Dict[str, Any]):
        """Add command result to history."""
        self.command_history.append(result)

        # Limit history size
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]


# Global CLI tools instance
cli_tools = CLITools()


# MCP tool definitions
def execute_command(command: str, **kwargs) -> Dict[str, Any]:
    """Execute shell command via MCP."""
    return cli_tools.execute_command(command, **kwargs)


def execute_script(script_path: str, **kwargs) -> Dict[str, Any]:
    """Execute script file via MCP."""
    return cli_tools.execute_script(script_path, **kwargs)


def get_system_info() -> Dict[str, Any]:
    """Get system information via MCP."""
    return cli_tools.get_system_info()


def list_processes(filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """List running processes via MCP."""
    return cli_tools.list_processes(filter_name)


def kill_process(pid: int, force: bool = False) -> Dict[str, Any]:
    """Kill process via MCP."""
    return cli_tools.kill_process(pid, force)

