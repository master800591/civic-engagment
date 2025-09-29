# CI/CD Workflows and Testing Documentation

## Overview

The Civic Engagement Platform uses GitHub Actions for continuous integration and deployment across multiple operating systems and Python versions.

## Supported Platforms

### Operating Systems
- **Ubuntu Latest** (Linux)
- **Windows Latest** 
- **macOS Latest**
- **Raspberry Pi** (ARM64/ARMHF via emulation)

### Python Versions
- Python 3.10
- Python 3.11 
- Python 3.12

## Workflow Structure

### Main CI Workflow (`.github/workflows/ci.yml`)

#### 1. Multi-Platform Testing
- **Matrix Strategy**: Tests across all OS/Python combinations
- **PyQt5 Support**: GUI testing with xvfb on Linux
- **ARM Emulation**: Raspberry Pi compatibility testing
- **Parallel Execution**: Fast feedback with fail-fast disabled

#### 2. Security Scanning
- **Bandit**: Python security vulnerability scanning
- **Safety**: Dependency vulnerability checking
- **Semgrep**: Advanced security pattern detection
- **Secret Detection**: Prevents accidental secret commits

#### 3. Code Quality
- **Linting**: flake8 for code style enforcement
- **Type Checking**: mypy for static type analysis
- **Formatting**: black for consistent code formatting
- **Import Sorting**: isort for organized imports
- **Complexity Analysis**: radon for code complexity metrics

#### 4. Build Verification
- **Import Testing**: Verifies all modules can be imported
- **Application Startup**: Tests basic application initialization
- **Cross-Platform Compatibility**: Ensures functionality across OSes

#### 5. Integration Testing
- **Comprehensive Tests**: Full module integration testing
- **Coverage Reporting**: Code coverage with codecov integration
- **Test Artifacts**: Preserves test results and reports

## Local Development Setup

### Quick Setup
```bash
# Run the setup script
./setup_testing.sh

# Or manually:
cd civic_desktop
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests Locally

#### Basic Test Run
```bash
cd civic_desktop
python -m pytest tests/ -v
```

#### With Coverage
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

#### GUI Tests (Linux)
```bash
xvfb-run python -m pytest tests/ -v
```

#### Specific Test Categories
```bash
# Run only unit tests
python -m pytest tests/test_comprehensive.py -v

# Run integration tests
python -m pytest tests/blockchain/ tests/users/ -v

# Run with timeout protection
python -m pytest tests/ --timeout=60 -v
```

### Security Testing
```bash
# Security vulnerability scan
bandit -r . --severity-level medium

# Dependency vulnerability check
safety check

# Check for secrets
./setup_testing.sh  # includes secret detection
```

### Code Quality Checks
```bash
# Code style linting
flake8 . --max-line-length=127

# Type checking
mypy . --ignore-missing-imports

# Code formatting
black --check .

# Import sorting
isort --check-only .
```

## CI Workflow Details

### Trigger Conditions
- **Push**: main, develop branches
- **Pull Request**: targeting main, develop branches
- **Manual**: workflow_dispatch for manual triggering

### Environment Variables
- `CIVIC_CONFIG`: Configuration file path for testing
- Platform-specific environment setup

### Artifact Preservation
- Security scan reports (JSON format)
- Test results (JUnit XML)
- Coverage reports (XML/HTML)

### Cache Strategy
- **pip cache**: Speeds up dependency installation
- **Key strategy**: OS-specific with requirements file hashing

## Test Architecture

### Test Categories

#### 1. Unit Tests (`test_comprehensive.py`)
- Individual module functionality
- Mock-based testing for isolated components
- Validation framework testing

#### 2. Integration Tests
- Cross-module functionality
- Database interaction testing
- API integration verification

#### 3. System Tests
- End-to-end workflow testing
- GUI component testing (with xvfb)
- Configuration system testing

#### 4. Security Tests
- Automated vulnerability scanning
- Secret detection
- Dependency security validation

### Test Utilities

#### Mock Support
- User authentication simulation
- Database operation mocking
- External service stubbing

#### Test Data Management
- Temporary file handling
- Test database isolation
- Configuration override support

## Platform-Specific Considerations

### Linux (Ubuntu)
- **GUI Testing**: xvfb for headless PyQt5 testing
- **System Dependencies**: libegl1-mesa, libgl1-mesa-glx
- **ARM Emulation**: qemu-user-static for Raspberry Pi testing

### Windows
- **PyQt5**: Windows-specific PyQt5 binaries
- **Path Handling**: Windows path compatibility
- **Service Dependencies**: Windows service simulation

### macOS
- **Framework Dependencies**: macOS-specific frameworks
- **GUI Testing**: Native macOS GUI testing
- **Permission Handling**: macOS security permission mocking

### Raspberry Pi (ARM)
- **Emulation**: QEMU-based ARM emulation on x86
- **Performance**: Adjusted timeouts for emulated environment
- **Resource Constraints**: Memory-optimized test execution

## Troubleshooting

### Common Issues

#### Import Errors
- **Solution**: Verify `sys.path` configuration in tests
- **Check**: Module availability and dependency installation

#### GUI Test Failures
- **Linux**: Ensure xvfb is running: `xvfb-run python -m pytest`
- **Windows/macOS**: Check display environment variables

#### Timeout Issues
- **Solution**: Increase timeout values in CI matrix
- **Local**: Use `--timeout=120` for longer tests

#### Security Scan Failures
- **False Positives**: Update `.bandit` configuration file
- **Real Issues**: Address security vulnerabilities promptly

### Performance Optimization

#### Test Execution Speed
- **Parallel Testing**: Use `pytest-xdist` for parallel execution
- **Test Filtering**: Use markers to run specific test categories
- **Mock Usage**: Mock external dependencies to avoid network calls

#### CI Performance
- **Cache Strategy**: Aggressive caching of dependencies
- **Matrix Optimization**: Strategic OS/Python combinations
- **Artifact Management**: Efficient artifact storage and retrieval

## Contributing to CI

### Adding New Tests
1. Follow existing test patterns in `test_comprehensive.py`
2. Use proper import error handling for optional dependencies
3. Add appropriate test markers for categorization
4. Include both positive and negative test cases

### Modifying CI Workflow
1. Test changes in a feature branch first
2. Verify all platform combinations work
3. Update documentation for any new requirements
4. Consider impact on CI execution time

### Security Considerations
1. Never commit real secrets or credentials
2. Use mock data for testing
3. Review security scan results in PR checks
4. Update security tools regularly

## Monitoring and Maintenance

### Regular Tasks
- **Weekly**: Review security scan results
- **Monthly**: Update dependencies and security tools
- **Quarterly**: Review and optimize CI performance
- **As needed**: Add support for new platforms or Python versions

### Metrics to Monitor
- **Test Success Rate**: Target >95% across all platforms
- **CI Execution Time**: Keep under 15 minutes total
- **Coverage**: Maintain >80% code coverage
- **Security Issues**: Zero unresolved high-severity issues

This CI/CD system ensures robust, secure, and cross-platform compatibility for the Civic Engagement Platform while maintaining high code quality standards.