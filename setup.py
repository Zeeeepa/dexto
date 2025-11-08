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
            
            # Step 7: Interactive Configuration
            self.logger.step(7, 8, "Configuration wizard...")
            if not self.args.no_setup:
                if not self.args.yes:
                    # Run interactive configuration wizard
                    config = self.interactive_configuration()
                    if config is None:
                        self.logger.error("Configuration cancelled by user")
                        return 1
                else:
                    # Non-interactive mode - validate existing keys
                    if not self.validate_api_keys():
                        self.logger.warning("No API keys found in non-interactive mode")
                        self.logger.info("Set environment variables or run without --yes flag")
            else:
                self.logger.info("Configuration skipped (use --no-setup)")
                # Still validate existing keys
                self.validate_api_keys()
            print()
            
            # Step 8: Final setup
            self.logger.step(8, 8, "Finalizing setup...")
            if not self.args.no_setup and not self.args.yes:
                response = input("Run additional setup wizard? (y/N): ").strip().lower()
                if response == 'y':
                    self.run_setup()
            self.logger.success("Setup complete!")
            print()
            
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
    
    def interactive_configuration(self):
        """Interactive configuration wizard for all variables"""
        print()
        print("=" * 60)
        print("  Dexto Configuration Wizard")
        print("=" * 60)
        print()
        print("This wizard will help you configure Dexto.")
        print("Press Enter to skip optional fields.")
        print()
        
        config = {}
        
        # Required API Keys Section
        print(Colors.color("REQUIRED: API Keys (at least one needed)", Colors.CYAN))
        print("-" * 60)
        print()
        
        required_keys = {
            'OPENAI_API_KEY': {
                'name': 'OpenAI API Key',
                'description': 'For GPT models (gpt-4, gpt-4o, etc.)',
                'placeholder': 'sk-...',
                'required': False  # At least one of the three
            },
            'ANTHROPIC_API_KEY': {
                'name': 'Anthropic API Key',
                'description': 'For Claude models (claude-sonnet, claude-opus)',
                'placeholder': 'sk-ant-...',
                'required': False
            },
            'GOOGLE_GENERATIVE_AI_API_KEY': {
                'name': 'Google Generative AI API Key',
                'description': 'For Gemini models (gemini-pro, gemini-flash)',
                'placeholder': 'AIza...',
                'required': False
            }
        }
        
        api_keys_configured = False
        for env_var, info in required_keys.items():
            current = os.environ.get(env_var, '')
            if current:
                print(f"✓ {info['name']}: Already configured")
                config[env_var] = current
                api_keys_configured = True
            else:
                print(f"\n{info['name']}")
                print(f"  Purpose: {info['description']}")
                print(f"  Format: {info['placeholder']}")
                value = input(f"  Enter key (or press Enter to skip): ").strip()
                if value:
                    config[env_var] = value
                    api_keys_configured = True
                    print(f"  ✓ {info['name']} saved")
        
        if not api_keys_configured:
            print()
            print(Colors.color("WARNING: No API keys configured!", Colors.YELLOW))
            print("You need at least one API key to use Dexto.")
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                return None
        
        # Optional Configuration Section
        print()
        print(Colors.color("OPTIONAL: Additional Configuration", Colors.CYAN))
        print("-" * 60)
        print()
        
        optional_configs = {
            'DEFAULT_LLM_PROVIDER': {
                'name': 'Default LLM Provider',
                'description': 'Which provider to use by default',
                'options': ['openai', 'anthropic', 'google'],
                'default': 'openai'
            },
            'DEFAULT_LLM_MODEL': {
                'name': 'Default LLM Model',
                'description': 'Which model to use by default',
                'examples': 'gpt-4o, claude-sonnet-4-5, gemini-2.0-flash',
                'default': 'gpt-4o'
            },
            'WEB_PORT': {
                'name': 'Web UI Port',
                'description': 'Port for the web interface',
                'default': '3000'
            },
            'API_PORT': {
                'name': 'API Server Port',
                'description': 'Port for the API server',
                'default': '3001'
            },
            'DISCORD_BOT_TOKEN': {
                'name': 'Discord Bot Token (OPTIONAL)',
                'description': 'For Discord integration',
                'placeholder': 'MTIzNDU2Nzg5...',
                'default': ''
            },
            'TELEGRAM_BOT_TOKEN': {
                'name': 'Telegram Bot Token (OPTIONAL)',
                'description': 'For Telegram integration',
                'placeholder': '123456789:ABC...',
                'default': ''
            },
            'LOG_LEVEL': {
                'name': 'Log Level (OPTIONAL)',
                'description': 'Logging verbosity',
                'options': ['debug', 'info', 'warn', 'error'],
                'default': 'info'
            },
            'TELEMETRY_ENABLED': {
                'name': 'Telemetry (OPTIONAL)',
                'description': 'Help improve Dexto by sharing anonymous usage data',
                'options': ['true', 'false'],
                'default': 'true'
            }
        }
        
        for env_var, info in optional_configs.items():
            current = os.environ.get(env_var, '')
            print(f"\n{info['name']} [OPTIONAL]")
            print(f"  Purpose: {info['description']}")
            
            if 'options' in info:
                print(f"  Options: {', '.join(info['options'])}")
            if 'examples' in info:
                print(f"  Examples: {info['examples']}")
            if 'placeholder' in info:
                print(f"  Format: {info['placeholder']}")
            
            default_val = current or info.get('default', '')
            if default_val:
                prompt = f"  Enter value [default: {default_val}]: "
            else:
                prompt = f"  Enter value (or press Enter to skip): "
            
            value = input(prompt).strip()
            
            if value:
                config[env_var] = value
                print(f"  ✓ Set to: {value}")
            elif default_val:
                config[env_var] = default_val
                print(f"  ✓ Using default: {default_val}")
        
        # Save configuration
        print()
        print("=" * 60)
        print("  Saving Configuration")
        print("=" * 60)
        print()
        
        self._save_configuration(config)
        
        return config
    
    def _save_configuration(self, config):
        """Save configuration to environment and config files"""
        # Create config directory
        config_dir = Path.home() / '.dexto' / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to JSON file
        config_file = config_dir / 'setup_config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        self.logger.success(f"Configuration saved to {config_file}")
        
        # Save to environment file
        env_file = config_dir / '.env'
        with open(env_file, 'w') as f:
            f.write("# Dexto Configuration\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        self.logger.success(f"Environment file saved to {env_file}")
        
        # Set environment variables for current session
        for key, value in config.items():
            os.environ[key] = value
        
        # Platform-specific persistent configuration
        if IS_WINDOWS:
            self._save_windows_env(config)
        else:
            self._save_unix_env(config)
    
    def _save_windows_env(self, config):
        """Save environment variables on Windows"""
        self.logger.info("Setting Windows environment variables...")
        for key, value in config.items():
            try:
                subprocess.run(
                    ['setx', key, value],
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError:
                self.logger.warning(f"Could not set {key} in Windows registry")
        
        self.logger.success("Windows environment variables configured")
        self.logger.info("Note: Restart your terminal for changes to take effect")
    
    def _save_unix_env(self, config):
        """Save environment variables on Unix systems"""
        # Detect shell config file
        shell_config = None
        home = Path.home()
        
        for config_file in ['.bashrc', '.zshrc', '.profile']:
            path = home / config_file
            if path.exists():
                shell_config = path
                break
        
        if not shell_config:
            # Default to .bashrc
            shell_config = home / '.bashrc'
        
        self.logger.info(f"Adding environment variables to {shell_config}")
        
        # Check if already configured
        try:
            with open(shell_config, 'r') as f:
                content = f.read()
            
            if '# Dexto Configuration' not in content:
                with open(shell_config, 'a') as f:
                    f.write("\n\n# Dexto Configuration\n")
                    for key, value in config.items():
                        f.write(f'export {key}="{value}"\n')
                
                self.logger.success(f"Configuration added to {shell_config}")
                self.logger.info("Run: source ~/.bashrc (or restart terminal)")
            else:
                self.logger.info("Configuration already exists in shell config")
        except Exception as e:
            self.logger.warning(f"Could not update shell config: {e}")
    
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
            return False
        
        return True
    
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
