# Windows Deployment Scripts

Automated batch scripts for deploying Dexto on Windows.

## Quick Start

```cmd
# 1. Install
scripts\windows\install.bat

# 2. Start
scripts\windows\start.bat

# 3. Open http://localhost:3000
```

## Scripts

| Script | Purpose |
|--------|---------|
| install.bat | Complete automated installation |
| start.bat | Start Dexto |
| stop.bat | Stop Dexto |
| status.bat | Check status |
| configure.bat | Configure settings |
| check_prerequisites.bat | Validate requirements |

## Prerequisites

- Windows 10/11
- Node.js 20+ ([Download](https://nodejs.org/))
- 4 GB RAM minimum
- 2 GB disk space

## Usage Examples

```cmd
# Start in CLI mode
scripts\windows\start.bat --mode cli

# Custom ports
scripts\windows\start.bat --web-port 8080

# Check if running
scripts\windows\status.bat
```

## Documentation

- Quick Start: QUICK_START.txt
- Full Instructions: INSTALL_INSTRUCTIONS.txt
- Deployment Guide: ../../docs/deployment/WINDOWS_DEPLOYMENT.md

## Troubleshooting

**"Node.js not found"**
- Install from https://nodejs.org/
- Restart terminal

**"dexto command not found"**  
- Close and reopen terminal
- Or restart computer

See INSTALL_INSTRUCTIONS.txt for more help.
