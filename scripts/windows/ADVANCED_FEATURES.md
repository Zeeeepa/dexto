# Windows Deployment Scripts - Advanced Features

This document describes the advanced features available in the Dexto Windows deployment scripts.

## 🚀 Advanced Installation Script

**File:** `install_advanced.bat`

### Features

#### 1. **Automatic Retry with Exponential Backoff**
- Retries failed operations up to 3 times
- Exponential backoff: 5s → 10s → 20s
- Handles transient network failures gracefully

```batch
# Automatically retries if network fails
scripts\windows\install_advanced.bat
```

#### 2. **Automatic Rollback on Failure**
- Backs up existing installation before upgrade
- Automatically restores on failure
- No manual cleanup required

**How it works:**
1. Backs up `node_modules` to `node_modules.backup`
2. Attempts installation
3. On failure: Removes failed installation, restores backup
4. On success: Removes backup

#### 3. **Detailed Error Logging**
- Timestamped logs for every operation
- Logs saved to: `%USERPROFILE%\.dexto\logs\installation_YYYYMMDD_HHMMSS.log`
- Includes error codes and recovery suggestions

**Log Format:**
```
[2025-11-08 18:45:23] [INFO] Starting advanced installation process
[2025-11-08 18:45:24] [1/8] Checking prerequisites...
[2025-11-08 18:45:25] [OK] Prerequisites verified
...
```

#### 4. **API Key Validation**
- Checks for configured API keys before completion
- Validates: OpenAI, Anthropic, Google AI
- Warns if no keys configured

#### 5. **Comprehensive Error Recovery**
- Detailed error messages with context
- Actionable recovery suggestions
- Common issues and solutions displayed

**Recovery Suggestions:**
- Network failure → Check internet connection
- Permission issues → Run as Administrator
- Disk space → Ensure 2+ GB free
- Antivirus → Temporarily disable and retry

## 📊 Comparison: Basic vs. Advanced

| Feature | Basic (`install.bat`) | Advanced (`install_advanced.bat`) |
|---------|----------------------|-----------------------------------|
| **Error Handling** | Stops on first error | Retries with backoff |
| **Rollback** | ❌ None | ✅ Automatic |
| **Logging** | Console only | Timestamped file logs |
| **Retry Logic** | ❌ None | ✅ 3 attempts with backoff |
| **API Validation** | ❌ None | ✅ Checks all providers |
| **Backup** | ❌ Manual | ✅ Automatic |
| **Recovery** | Manual cleanup | Automatic restore |

## 🎯 When to Use Each

### Use **Basic Installation** (`install.bat`) when:
- ✅ First-time installation
- ✅ Stable network connection
- ✅ Quick setup needed
- ✅ Don't need detailed logs

### Use **Advanced Installation** (`install_advanced.bat`) when:
- ✅ Upgrading existing installation
- ✅ Unstable network connection
- ✅ Production deployment
- ✅ Need audit trail (logs)
- ✅ Want automatic rollback protection

## 🔧 Usage

### Advanced Installation
```cmd
# Run advanced installer
scripts\windows\install_advanced.bat

# Installation will:
# 1. Check prerequisites
# 2. Backup existing installation
# 3. Install with retry logic
# 4. Validate API keys
# 5. Run setup wizard
# 6. Clean up backup on success
# 7. Rollback on failure
```

### View Installation Logs
```cmd
# Logs are saved to:
%USERPROFILE%\.dexto\logs\installation_YYYYMMDD_HHMMSS.log

# View latest log:
type %USERPROFILE%\.dexto\logs\installation_*.log | more
```

## 🛡️ Error Handling Examples

### Example 1: Network Failure with Auto-Retry
```
[1/8] Installing dependencies (with retry)...
[ATTEMPT 1/3] Installing...
[WARNING] Attempt 1 failed
[INFO] Retrying in 5 seconds...
[ATTEMPT 2/3] Installing...
[OK] Dependencies installed
```

### Example 2: Build Failure with Rollback
```
[4/8] Building all packages...
[ATTEMPT 1/3] Building...
[ERROR] Build failed after 3 attempts

========================================
  Rollback in Progress
========================================

Removing failed installation...
Restoring previous installation...
[OK] Previous installation restored

Installation failed. Check log file for details:
C:\Users\username\.dexto\logs\installation_20251108_184523.log
```

## 📝 Log File Analysis

### Log File Location
```
%USERPROFILE%\.dexto\logs\installation_YYYYMMDD_HHMMSS.log
```

### Log File Contents
- Timestamp for every operation
- Error codes and error levels
- Recovery actions taken
- Rollback operations performed
- Final installation status

### Example Log Excerpt
```
[2025-11-08 18:45:23] [INFO] Starting advanced installation process
[2025-11-08 18:45:24] [1/8] Checking prerequisites...
[2025-11-08 18:45:25] [OK] Prerequisites verified
[2025-11-08 18:45:26] [2/8] Checking for existing installation...
[2025-11-08 18:45:26] [INFO] Existing installation found
[2025-11-08 18:45:27] [INFO] Creating backup of existing installation...
[2025-11-08 18:45:28] [OK] Backup created successfully
[2025-11-08 18:45:29] [3/8] Installing dependencies...
[2025-11-08 18:45:29] [ATTEMPT 1/3] Running pnpm install...
[2025-11-08 18:46:15] [OK] Dependencies installed successfully
...
```

## 🚨 Troubleshooting

### Installation Fails Even with Retries
1. Check log file for specific error
2. Ensure stable internet connection
3. Run as Administrator
4. Temporarily disable antivirus
5. Ensure 2+ GB free disk space

### Rollback Fails
If automatic rollback fails:
1. Check log file: `%USERPROFILE%\.dexto\logs\installation_*.log`
2. Manually restore: `move node_modules.backup node_modules`
3. Contact support with log file

### API Keys Not Detected
The validator checks environment variables:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_GENERATIVE_AI_API_KEY`

To configure:
```cmd
scripts\windows\configure.bat
```

## 🔮 Future Enhancements

Planned features for advanced installation:

- [ ] Health check validation after installation
- [ ] Automatic LLM provider failover configuration
- [ ] Pre-installation disk space check
- [ ] Dependency version compatibility check
- [ ] Automatic cleanup of old log files
- [ ] Installation performance metrics
- [ ] Email/webhook notification on completion

## 📚 Related Documentation

- [Basic Installation](README.md)
- [Quick Start Guide](QUICK_START.txt)
- [Full Installation Instructions](INSTALL_INSTRUCTIONS.txt)
- [Deployment Gaps Analysis](../../docs/DEPLOYMENT_GAPS_ANALYSIS.md)

---

**Note:** Both basic and advanced installers are production-ready. Choose based on your deployment requirements and risk tolerance.

