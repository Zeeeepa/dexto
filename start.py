#!/usr/bin/env python3
"""
Dexto Universal Start Script
Cross-platform process management for Dexto

Features:
- Start in any mode (web, cli, server, discord, telegram, mcp)
- Stop running instances
- Status checking
- Background/daemon mode
- Port conflict detection
- Configuration management
- Cross-platform support (Windows, Linux, macOS)

Usage:
    python start.py                          # Start in web mode
    python start.py --mode cli               # Start in CLI mode
    python start.py --mode server            # API server only
    python start.py --daemon                 # Background mode
    python start.py --status                 # Check status
    python start.py --stop                   # Stop running instance
    python start.py --configure              # Interactive configuration
"""

import os
import sys
import subprocess
import signal
import psutil
import argparse
import time
from pathlib import Path
import platform
import json

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

class Colors:
    """ANSI color codes"""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    
    @staticmethod
    def color(text, color_code):
        if IS_WINDOWS:
            return text
        return f"{color_code}{text}{Colors.RESET}"

class DextoProcess:
    """Manage Dexto processes"""
    
    def __init__(self):
        self.dexto_home = Path.home() / '.dexto'
        self.pid_file = self.dexto_home / 'dexto.pid'
        self.dexto_home.mkdir(parents=True, exist_ok=True)
    
    def get_dexto_processes(self):
        """Find all running Dexto processes"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('dexto' in str(arg).lower() for arg in cmdline):
                        processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass
        
        return processes
    
    def save_pid(self, pid, mode, ports):
        """Save process information"""
        data = {
            'pid': pid,
            'mode': mode,
            'ports': ports,
            'start_time': time.time()
        }
        
        with open(self.pid_file, 'w') as f:
            json.dump(data, f)
    
    def load_pid(self):
        """Load saved process information"""
        if not self.pid_file.exists():
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def clear_pid(self):
        """Remove PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def is_port_in_use(self, port):
        """Check if port is in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False

class DextoManager:
    """Main Dexto management class"""
    
    def __init__(self, args):
        self.args = args
        self.process_mgr = DextoProcess()
    
    def start(self):
        """Start Dexto in specified mode"""
        mode = self.args.mode
        web_port = self.args.web_port
        api_port = self.args.api_port
        
        print()
        print(Colors.color(f"Starting Dexto in {mode} mode...", Colors.CYAN))
        print()
        
        # Check for existing processes
        existing = self.process_mgr.get_dexto_processes()
        if existing and not self.args.force:
            print(Colors.color("[WARNING] Dexto is already running", Colors.YELLOW))
            print()
            print("Options:")
            print("  1. Stop existing instance: python start.py --stop")
            print("  2. Force restart: python start.py --force")
            return 1
        
        # Port conflict detection
        if mode == 'web':
            if self.process_mgr.is_port_in_use(web_port):
                print(Colors.color(f"[WARNING] Port {web_port} is already in use", Colors.YELLOW))
                response = input("Continue anyway? (y/N): ").strip().lower()
                if response != 'y':
                    return 1
        
        if mode in ['web', 'server'] and self.process_mgr.is_port_in_use(api_port):
            print(Colors.color(f"[WARNING] Port {api_port} is already in use", Colors.YELLOW))
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                return 1
        
        # Build command
        cmd = ['dexto', '--mode', mode]
        
        if mode == 'web':
            cmd.extend(['--web-port', str(web_port), '--api-port', str(api_port)])
            print(f"Web UI: http://localhost:{web_port}")
            print(f"API Server: http://localhost:{api_port}")
        elif mode == 'server':
            cmd.extend(['--api-port', str(api_port)])
            print(f"API Server: http://localhost:{api_port}")
        
        if self.args.agent:
            cmd.extend(['--agent', self.args.agent])
        
        if self.args.config:
            cmd.extend(['--config', self.args.config])
        
        # Add extra args
        if self.args.extra_args:
            cmd.extend(self.args.extra_args)
        
        print()
        print(Colors.color(f"Command: {' '.join(cmd)}", Colors.CYAN))
        print()
        
        # Start process
        try:
            if self.args.daemon:
                # Background mode
                print("Starting in background mode...")
                
                if IS_WINDOWS:
                    # Windows background process
                    CREATE_NEW_PROCESS_GROUP = 0x00000200
                    DETACHED_PROCESS = 0x00000008
                    
                    proc = subprocess.Popen(
                        cmd,
                        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    # Unix daemon
                    proc = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        preexec_fn=os.setpgrp
                    )
                
                # Save PID
                ports = {'web': web_port, 'api': api_port} if mode == 'web' else {'api': api_port}
                self.process_mgr.save_pid(proc.pid, mode, ports)
                
                print(Colors.color(f"[OK] Dexto started (PID: {proc.pid})", Colors.GREEN))
                print()
                print("Check status: python start.py --status")
                print("Stop: python start.py --stop")
                
            else:
                # Foreground mode
                print("Press Ctrl+C to stop")
                print()
                
                proc = subprocess.Popen(cmd)
                
                # Save PID
                ports = {'web': web_port, 'api': api_port} if mode == 'web' else {'api': api_port}
                self.process_mgr.save_pid(proc.pid, mode, ports)
                
                # Wait for process
                proc.wait()
                
                print()
                print("Dexto stopped.")
                self.process_mgr.clear_pid()
            
            return 0
            
        except KeyboardInterrupt:
            print()
            print("Stopping Dexto...")
            self.process_mgr.clear_pid()
            return 0
        
        except FileNotFoundError:
            print(Colors.color("[ERROR] dexto command not found", Colors.RED))
            print()
            print("Please run setup first:")
            print("  python setup.py")
            return 1
        
        except Exception as e:
            print(Colors.color(f"[ERROR] Failed to start: {e}", Colors.RED))
            return 1
    
    def stop(self):
        """Stop running Dexto processes"""
        print()
        print("Stopping Dexto processes...")
        print()
        
        processes = self.process_mgr.get_dexto_processes()
        
        if not processes:
            print(Colors.color("[INFO] No Dexto processes found running", Colors.CYAN))
            self.process_mgr.clear_pid()
            return 0
        
        killed = 0
        for proc in processes:
            try:
                print(f"Stopping process {proc.pid}...")
                
                if self.args.force:
                    proc.kill()
                else:
                    proc.terminate()
                    try:
                        proc.wait(timeout=10)
                    except psutil.TimeoutExpired:
                        proc.kill()
                
                killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(Colors.color(f"[WARNING] Could not stop process {proc.pid}: {e}", Colors.YELLOW))
        
        self.process_mgr.clear_pid()
        
        if killed > 0:
            print()
            print(Colors.color(f"[OK] Stopped {killed} process(es)", Colors.GREEN))
        
        return 0
    
    def status(self):
        """Show status of Dexto processes"""
        print()
        print("=" * 50)
        print("  Dexto Status")
        print("=" * 50)
        print()
        
        # Check saved PID info
        pid_info = self.process_mgr.load_pid()
        if pid_info:
            print(f"Saved PID: {pid_info['pid']}")
            print(f"Mode: {pid_info['mode']}")
            print(f"Ports: {pid_info['ports']}")
            
            # Check if still running
            try:
                proc = psutil.Process(pid_info['pid'])
                if proc.is_running():
                    uptime = time.time() - pid_info['start_time']
                    hours = int(uptime // 3600)
                    minutes = int((uptime % 3600) // 60)
                    print(f"Uptime: {hours}h {minutes}m")
                    print(f"Status: {Colors.color('RUNNING', Colors.GREEN)}")
                else:
                    print(f"Status: {Colors.color('NOT RUNNING', Colors.RED)}")
                    self.process_mgr.clear_pid()
            except psutil.NoSuchProcess:
                print(f"Status: {Colors.color('NOT RUNNING', Colors.RED)}")
                self.process_mgr.clear_pid()
            
            print()
        
        # Find all Dexto processes
        processes = self.process_mgr.get_dexto_processes()
        
        if processes:
            print(f"Found {len(processes)} Dexto process(es):")
            print()
            
            for proc in processes:
                try:
                    print(f"PID: {proc.pid}")
                    print(f"  Command: {' '.join(proc.cmdline())}")
                    print(f"  CPU: {proc.cpu_percent()}%")
                    print(f"  Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
                    print()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            print(Colors.color("No Dexto processes running", Colors.YELLOW))
        
        # Check ports
        print("Port Status:")
        for port in [3000, 3001]:
            if self.process_mgr.is_port_in_use(port):
                print(f"  Port {port}: {Colors.color('IN USE', Colors.GREEN)}")
            else:
                print(f"  Port {port}: {Colors.color('AVAILABLE', Colors.CYAN)}")
        
        print()
        return 0
    
    def configure(self):
        """Interactive configuration"""
        print()
        print("=" * 50)
        print("  Dexto Configuration")
        print("=" * 50)
        print()
        
        print("Configuration options:")
        print()
        print("  1. Run full setup wizard (recommended)")
        print("  2. Set API keys")
        print("  3. Configure default agent")
        print("  4. View current configuration")
        print("  5. Exit")
        print()
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            return self._run_setup_wizard()
        elif choice == '2':
            return self._configure_api_keys()
        elif choice == '3':
            return self._configure_agent()
        elif choice == '4':
            return self._view_config()
        else:
            return 0
    
    def _run_setup_wizard(self):
        """Run dexto setup"""
        print()
        print("Running setup wizard...")
        try:
            subprocess.run(['dexto', 'setup'])
            return 0
        except FileNotFoundError:
            print(Colors.color("[ERROR] dexto command not found", Colors.RED))
            return 1
    
    def _configure_api_keys(self):
        """Configure API keys interactively"""
        print()
        print("=" * 50)
        print("  API Key Configuration")
        print("=" * 50)
        print()
        print("Enter your API keys (leave blank to skip):")
        print()
        
        keys = {
            'OPENAI_API_KEY': 'OpenAI API Key',
            'ANTHROPIC_API_KEY': 'Anthropic API Key',
            'GOOGLE_GENERATIVE_AI_API_KEY': 'Google Generative AI API Key'
        }
        
        for env_var, prompt in keys.items():
            value = input(f"{prompt}: ").strip()
            if value:
                os.environ[env_var] = value
                
                # Persist to shell config
                if IS_WINDOWS:
                    subprocess.run(['setx', env_var, value], capture_output=True)
                    print(Colors.color(f"[OK] {prompt} saved (Windows)", Colors.GREEN))
                else:
                    shell_config = Path.home() / '.bashrc'
                    if not shell_config.exists():
                        shell_config = Path.home() / '.zshrc'
                    
                    with open(shell_config, 'a') as f:
                        f.write(f'\nexport {env_var}="{value}"\n')
                    
                    print(Colors.color(f"[OK] {prompt} saved to {shell_config}", Colors.GREEN))
        
        print()
        print("API keys configured. Restart your terminal for changes to take effect.")
        return 0
    
    def _configure_agent(self):
        """Configure default agent"""
        print()
        try:
            result = subprocess.run(
                ['dexto', 'list-agents', '--installed'],
                capture_output=True,
                text=True
            )
            print(result.stdout)
        except FileNotFoundError:
            print(Colors.color("[ERROR] dexto command not found", Colors.RED))
            return 1
        
        agent_name = input("Enter default agent name: ").strip()
        if agent_name:
            try:
                subprocess.run(
                    ['dexto', 'setup', '--default-agent', agent_name, '--no-interactive']
                )
                print(Colors.color(f"[OK] Default agent set to: {agent_name}", Colors.GREEN))
            except:
                print(Colors.color("[ERROR] Failed to set default agent", Colors.RED))
                return 1
        
        return 0
    
    def _view_config(self):
        """View current configuration"""
        print()
        print("Current configuration:")
        print()
        
        config_file = Path.home() / '.dexto' / 'config' / 'global.yml'
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                print(f.read())
        else:
            print(Colors.color("[INFO] No configuration file found", Colors.CYAN))
            print("Run setup wizard to create configuration:")
            print("  python start.py --configure")
        
        print()
        return 0

def main():
    parser = argparse.ArgumentParser(
        description='Dexto Universal Start Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py                          # Start in web mode
  python start.py --mode cli               # Start in CLI mode
  python start.py --daemon                 # Background mode
  python start.py --status                 # Check status
  python start.py --stop                   # Stop running instance
        """
    )
    
    # Action flags
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '--status',
        action='store_true',
        help='Show status of running processes'
    )
    action_group.add_argument(
        '--stop',
        action='store_true',
        help='Stop running Dexto processes'
    )
    action_group.add_argument(
        '--configure',
        action='store_true',
        help='Interactive configuration menu'
    )
    
    # Start options
    parser.add_argument(
        '--mode',
        type=str,
        choices=['web', 'cli', 'server', 'discord', 'telegram', 'mcp'],
        default='web',
        help='Operational mode (default: web)'
    )
    
    parser.add_argument(
        '--web-port',
        type=int,
        default=3000,
        help='Web UI port (default: 3000)'
    )
    
    parser.add_argument(
        '--api-port',
        type=int,
        default=3001,
        help='API server port (default: 3001)'
    )
    
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run in background/daemon mode'
    )
    
    parser.add_argument(
        '--agent',
        type=str,
        help='Specify agent to use'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom config file'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force restart if already running'
    )
    
    parser.add_argument(
        'extra_args',
        nargs='*',
        help='Additional arguments to pass to dexto'
    )
    
    args = parser.parse_args()
    
    manager = DextoManager(args)
    
    # Execute requested action
    if args.status:
        exit_code = manager.status()
    elif args.stop:
        exit_code = manager.stop()
    elif args.configure:
        exit_code = manager.configure()
    else:
        exit_code = manager.start()
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()

