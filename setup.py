#!/usr/bin/env python3
"""
Dexto Universal Setup Script
Cross-platform installation with advanced error handling

Features:
- Automatic prerequisite checking (Node.js, npm, pnpm)
- Retry logic with exponential backoff
- Automatic rollback on failure
- Detailed timestamped logging
- API key validation
- Cross-platform support (Windows, Linux, macOS)
- Interactive configuration wizard

Usage:
    python setup.py                    # Basic installation
    python setup.py --advanced         # Advanced mode with retry/rollback
    python setup.py --no-setup         # Skip interactive setup
    python setup.py --log-dir PATH     # Custom log directory
"""

import os
import sys
import subprocess
import shutil
import time
import argparse
from pathlib import Path
from datetime import datetime
import platform
import json

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    
    @staticmethod
    def color(text, color_code):
        if IS_WINDOWS:
            # Windows may not support ANSI colors in all terminals
            return text
        return f"{color_code}{text}{Colors.RESET}"

class Logger:
    """Logging utility with file and console output"""
    
    def __init__(self, log_dir=None):
        if log_dir is None:
            log_dir = Path.home() / '.dexto' / 'logs'
        else:
            log_dir = Path(log_dir)
        
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = log_dir / f'installation_{timestamp}.log'
        
    def _format_message(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp}] [{level}] {message}"
    
    def log(self, level, message, color=None):
        """Log message to both file and console"""
        formatted = self._format_message(level, message)
        
        # Write to file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(formatted + '\n')
        
        # Print to console
        if color and not IS_WINDOWS:
            print(Colors.color(message, color))
        else:
            print(message)
    
    def info(self, message):
        self.log('INFO', message, Colors.CYAN)
    
    def success(self, message):
        self.log('OK', f"[OK] {message}", Colors.GREEN)
    
    def warning(self, message):
        self.log('WARNING', f"[WARNING] {message}", Colors.YELLOW)
    
    def error(self, message):
        self.log('ERROR', f"[ERROR] {message}", Colors.RED)
    
    def step(self, current, total, message):
        self.info(f"[{current}/{total}] {message}")

class DextoSetup:
    """Main setup orchestrator"""
    
    def __init__(self, args):
        self.args = args
        self.logger = Logger(args.log_dir)
        self.project_root = Path(__file__).parent
        self.backup_dir = self.project_root / 'node_modules.backup'
        self.node_modules = self.project_root / 'node_modules'
        self.max_retries = 3 if args.advanced else 1
        
    def run(self):
        """Execute installation process"""
        print()
        print("=" * 50)
        print("  Dexto Universal Setup")
        print("=" * 50)
        print()
        
        self.logger.info(f"Log file: {self.logger.log_file}")
        self.logger.info(f"Platform: {platform.system()} {platform.release()}")
        self.logger.info(f"Advanced mode: {self.args.advanced}")
        print()
        
        try:
            # Step 1: Check prerequisites
            self.logger.step(1, 8, "Checking prerequisites...")
            if not self.check_prerequisites():
                return 1
            self.logger.success("Prerequisites verified")
            print()
            
            # Step 2: Backup existing installation
            self.logger.step(2, 8, "Checking for existing installation...")
            if self.node_modules.exists():
                self.logger.info("Existing installation detected")
                
                if not self.args.yes:
                    response = input("Reinstall? (y/N): ").strip().lower()
                    if response != 'y':
                        self.logger.info("Installation cancelled by user")
                        return 0
                
                if self.args.advanced:
                    self.create_backup()
            else:
                self.logger.info("Fresh installation")
            print()
            
            # Step 3: Install dependencies
            self.logger.step(3, 8, "Installing dependencies...")
            if not self.install_dependencies():
                self.logger.error("Failed to install dependencies")
                if self.args.advanced:
                    self.rollback()
                return 1
            self.logger.success("Dependencies installed")
            print()
            
            # Step 4: Build packages
            self.logger.step(4, 8, "Building packages...")
            if not self.build_packages():
                self.logger.error("Failed to build packages")
                if self.args.advanced:
                    self.rollback()
                return 1
            self.logger.success("Build completed")
            print()
            
            # Step 5: Install CLI globally
            self.logger.step(5, 8, "Installing CLI globally...")
            if not self.install_cli():
                self.logger.error("Failed to install CLI")
                if self.args.advanced:
                    self.rollback()
                return 1
            self.logger.success("CLI installed globally")
            print()
            
            # Step 6: Verify installation
            self.logger.step(6, 8, "Verifying installation...")
            version = self.verify_installation()
            if version:
                self.logger.success(f"Dexto {version} installed successfully")
            else:
                self.logger.warning("dexto command not found in PATH")
                self.logger.warning("You may need to restart your terminal")
            print()
            
            # Step 7: Validate API keys
            self.logger.step(7, 8, "Validating API keys...")
            self.validate_api_keys()
            print()
            
            # Step 8: Run setup wizard
            if not self.args.no_setup:
                self.logger.step(8, 8, "Initial configuration...")
                if not self.args.yes:
                    response = input("Run setup wizard now? (Y/n): ").strip().lower()
                    if response != 'n':
                        self.run_setup()
                else:
                    self.run_setup()
            else:
                self.logger.info("Setup skipped")
            
            # Clean up backup on success
            if self.args.advanced and self.backup_dir.exists():
                self.logger.info("Removing backup")
                shutil.rmtree(self.backup_dir)
            
            # Success message
            print()
            print("=" * 50)
            print("  Installation Complete!")
            print("=" * 50)
            print()
            print("Next steps:")
            print("  1. Open a new terminal")
            print("  2. Run: dexto")
            print("  3. Access Web UI at http://localhost:3000")
            print()
            print(f"Installation log: {self.logger.log_file}")
            print()
            
            return 0
            
        except KeyboardInterrupt:
            self.logger.error("Installation cancelled by user")
            if self.args.advanced:
                self.rollback()
            return 1
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            if self.args.advanced:
                self.rollback()
            return 1
    
    def check_prerequisites(self):
        """Check for Node.js, npm, and pnpm"""
        checks = {
            'node': ('node', '--version'),
            'npm': ('npm', '--version'),
            'pnpm': ('pnpm', '--version')
        }
        
        all_ok = True
        
        for name, cmd in checks.items():
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.logger.success(f"{name} {version} found")
                else:
                    self.logger.error(f"{name} not found")
                    all_ok = False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.logger.error(f"{name} not found")
                all_ok = False
                
                # Auto-install pnpm if npm exists
                if name == 'pnpm' and 'npm' in checks:
                    self.logger.info("Attempting to install pnpm...")
                    try:
                        subprocess.run(
                            ['npm', 'install', '-g', 'pnpm'],
                            check=True,
                            timeout=120
                        )
                        self.logger.success("pnpm installed successfully")
                        all_ok = True
                    except:
                        self.logger.error("Failed to install pnpm")
        
        if not all_ok:
            print()
            self.logger.error("Missing prerequisites. Please install:")
            print("  - Node.js 20+: https://nodejs.org/")
            print("  - pnpm: npm install -g pnpm")
        
        return all_ok
    
    def create_backup(self):
        """Backup existing node_modules"""
        if self.node_modules.exists():
            self.logger.info("Creating backup...")
            
            # Remove old backup if exists
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            shutil.move(str(self.node_modules), str(self.backup_dir))
            self.logger.success("Backup created")
    
    def install_dependencies(self):
        """Install dependencies with retry logic"""
        return self._retry_operation(
            "pnpm install",
            ['pnpm', 'install'],
            "Installing dependencies"
        )
    
    def build_packages(self):
        """Build all packages with retry logic"""
        return self._retry_operation(
            "pnpm run build:all",
            ['pnpm', 'run', 'build:all'],
            "Building packages"
        )
    
    def install_cli(self):
        """Install CLI globally"""
        return self._retry_operation(
            "pnpm run install-cli",
            ['pnpm', 'run', 'install-cli'],
            "Installing CLI"
        )
    
    def _retry_operation(self, description, cmd, operation_name):
        """Execute command with retry logic"""
        retry_delay = 5
        
        for attempt in range(1, self.max_retries + 1):
            try:
                if self.max_retries > 1:
                    self.logger.info(f"[ATTEMPT {attempt}/{self.max_retries}] {operation_name}...")
                
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    check=True,
                    timeout=600,  # 10 minutes max
                    capture_output=True,
                    text=True
                )
                
                # Log output to file
                if result.stdout:
                    self.logger.log('OUTPUT', result.stdout)
                
                return True
                
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Attempt {attempt} failed with exit code {e.returncode}")
                
                if e.stderr:
                    self.logger.log('ERROR_OUTPUT', e.stderr)
                
                if attempt < self.max_retries:
                    self.logger.warning(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    return False
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"Attempt {attempt} timed out")
                if attempt < self.max_retries:
                    self.logger.warning(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return False
        
        return False
    
    def verify_installation(self):
        """Verify dexto CLI is available"""
        try:
            result = subprocess.run(
                ['dexto', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def validate_api_keys(self):
        """Check for configured API keys"""
        keys = {
            'OPENAI_API_KEY': 'OpenAI',
            'ANTHROPIC_API_KEY': 'Anthropic',
            'GOOGLE_GENERATIVE_AI_API_KEY': 'Google'
        }
        
        found_any = False
        
        for env_var, provider in keys.items():
            if os.environ.get(env_var):
                self.logger.success(f"{provider} API key configured")
                found_any = True
        
        if not found_any:
            self.logger.warning("No API keys configured")
            self.logger.warning("You'll need to configure API keys to use Dexto")
            print()
            print("Configure API keys:")
            print("  1. Run: dexto setup")
            print("  2. Or set environment variables:")
            print("     export OPENAI_API_KEY='sk-...'")
            print("     export ANTHROPIC_API_KEY='sk-ant-...'")
    
    def run_setup(self):
        """Run interactive setup wizard"""
        self.logger.info("Running setup wizard...")
        try:
            subprocess.run(
                ['dexto', 'setup'],
                cwd=self.project_root,
                timeout=300
            )
        except subprocess.TimeoutExpired:
            self.logger.warning("Setup wizard timed out")
        except FileNotFoundError:
            self.logger.warning("dexto command not found, skipping setup")
    
    def rollback(self):
        """Rollback failed installation"""
        self.logger.error("Installation failed. Rolling back...")
        print()
        print("=" * 50)
        print("  Rollback in Progress")
        print("=" * 50)
        print()
        
        # Remove failed installation
        if self.node_modules.exists():
            self.logger.info("Removing failed installation...")
            shutil.rmtree(self.node_modules)
        
        # Restore backup
        if self.backup_dir.exists():
            self.logger.info("Restoring backup...")
            shutil.move(str(self.backup_dir), str(self.node_modules))
            self.logger.success("Previous installation restored")
        else:
            self.logger.info("No backup to restore")
        
        print()
        print("Installation failed. Check log file:")
        print(f"  {self.logger.log_file}")
        print()
        print("Common issues and solutions:")
        print("  - Network failure: Check internet connection and retry")
        print("  - Permission issues: Run with sudo/admin privileges")
        print("  - Disk space: Ensure 2+ GB free space")
        print("  - Antivirus: Temporarily disable and retry")
        print()

def main():
    parser = argparse.ArgumentParser(
        description='Dexto Universal Setup Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup.py                    # Basic installation
  python setup.py --advanced         # Advanced mode with retry/rollback
  python setup.py --no-setup         # Skip interactive setup
  python setup.py --yes              # Non-interactive mode
        """
    )
    
    parser.add_argument(
        '--advanced',
        action='store_true',
        help='Enable advanced mode with retry logic and rollback'
    )
    
    parser.add_argument(
        '--no-setup',
        action='store_true',
        help='Skip interactive setup wizard'
    )
    
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Answer yes to all prompts (non-interactive)'
    )
    
    parser.add_argument(
        '--log-dir',
        type=str,
        help='Custom directory for log files'
    )
    
    args = parser.parse_args()
    
    setup = DextoSetup(args)
    exit_code = setup.run()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()

