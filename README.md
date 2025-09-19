# Synthetic Insights Generator

A comprehensive Python orchestrator that creates realistic Red Hat Insights archives with synthetic PCP performance data and cloud metadata for testing and development.

## Repository

📂 **C Binary Source Code**: [https://github.com/upadhyeammit/synthetic-pcp-generator](https://github.com/upadhyeammit/synthetic-pcp-generator)

## Overview

**Synthetic Insights Generator** is the main entry point for creating complete test Insights archives that include:
- **Synthetic PCP performance data** (via native C binary)
- **Embedded cloud metadata** (AWS instance information)
- **Realistic system metrics** across 4 different utilization patterns
- **Complete archive structure** compatible with Red Hat Insights processing

This tool is designed for testing ROS (Resource Optimization Service) recommendations, validating performance analysis algorithms, and creating reproducible test datasets.

## Features

- 🎯 **Complete Insights Archive Processing** - Full workflow from input to synthetic output
- 🔧 **Native PCP Integration** - Uses high-performance C binary for PCP data generation
- ☁️ **Embedded Cloud Metadata** - Self-contained AWS metadata (no external dependencies)
- 📊 **Four System State Patterns** - Idle, Optimized, Under Pressure, Undersized
- 🛡️ **Sanitized Data** - All sensitive information replaced with mock values
- 🔄 **Flexible Binary Path** - Configurable path to synthetic-pcp-generator binary
- ⚡ **Fast Processing** - Efficient archive manipulation and repackaging

## Requirements

### Python Dependencies
```bash
# The tool uses only Python standard library modules
# No additional pip packages required
```

### System Requirements
```bash
# For PCP data generation
sudo dnf install pcp-devel pcp-import-devel  # Fedora/RHEL/CentOS
sudo apt-get install libpcp3-dev libpcp-import1-dev  # Ubuntu/Debian

# For archive processing
sudo dnf install tar xz-utils  # Usually already installed
```

### Binary Dependency
- **synthetic-pcp-generator** - Native C binary (see compilation instructions below)

## Installation

### 1. Ensure Dependencies
```bash
# Install PCP development libraries
sudo dnf install pcp-devel pcp-import-devel

# Compile the C binary (if not already done)
gcc -o synthetic-pcp-generator synthetic-pcp-generator.c -lpcp -lpcp_import
```

### 2. Make Executable
```bash
chmod +x synthetic-insights-generator.py
```

### 3. Verify Installation
```bash
./synthetic-insights-generator.py --list-patterns
```

## System State Patterns

| Pattern | Description | CPU Usage | Memory Usage | PSI Pressure | Use Case |
|---------|-------------|-----------|--------------|--------------|-----------|
| **idle** | Very low utilization | ~0.15% | ~0.1% used | None | Test downsizing recommendations |
| **optimized** | Balanced utilization | ~50% | ~36.4% used | Low | Validate optimal scenarios |
| **under_pressure** | Moderate load with pressure | ~10% | ~12.2% used | High | Test pressure detection |
| **undersized** | High utilization | ~90% | ~96.9% used | High | Test scaling recommendations |

## Usage

### Basic Syntax
```bash
./synthetic-insights-generator.py [input_archive] [OPTIONS]
```

### Command Line Options

#### Required Arguments
- `input_archive` - Input Insights `.tar.gz` archive to process

#### Optional Arguments
- `--pattern {idle,optimized,under_pressure,undersized}` - System state pattern (default: undersized)
- `--output OUTPUT` - Output archive name without `.tar.gz` extension
- `--pcp-generator-path PATH` - Path to synthetic-pcp-generator binary (default: `./synthetic-pcp-generator`)
- `--list-patterns` - List all available patterns and exit

### Examples

#### List Available Patterns
```bash
./synthetic-insights-generator.py --list-patterns
```

#### Basic Processing with Default Pattern (Undersized)
```bash
./synthetic-insights-generator.py input_archive.tar.gz
```

#### Generate Specific System States
```bash
# Create idle system simulation
./synthetic-insights-generator.py input_archive.tar.gz --pattern idle --output idle_test

# Create optimized system simulation  
./synthetic-insights-generator.py input_archive.tar.gz --pattern optimized --output balanced_system

# Create pressure simulation
./synthetic-insights-generator.py input_archive.tar.gz --pattern under_pressure --output pressure_test

# Create high utilization simulation
./synthetic-insights-generator.py input_archive.tar.gz --pattern undersized --output busy_system
```

#### Custom Binary Path
```bash
# Use binary from different location
./synthetic-insights-generator.py input_archive.tar.gz --pattern idle \
    --pcp-generator-path /usr/local/bin/synthetic-pcp-generator

# Use binary with different name
./synthetic-insights-generator.py input_archive.tar.gz --pattern optimized \
    --pcp-generator-path ../tools/my-pcp-generator
```

### Sample Output
```bash
$ ./synthetic-insights-generator.py test-archive.tar.gz --pattern idle --output idle_system

🚀 Processing Insights archive with Synthetic PCP Data + Embedded Cloud Metadata
📂 Input: test-archive.tar.gz
📊 Pattern: idle - Very low utilization (~0.15% CPU, ~99.9% memory free)
☁️ Cloud: Synthetic metadata (self-contained)
📂 Output: idle_system

✅ Native C PMI program ready: ./synthetic-pcp-generator
✅ Cloud metadata: Embedded in script (self-contained)
✅ Supported patterns: idle, optimized, under_pressure, undersized
📂 Extracting Insights archive: test-archive.tar.gz
✅ Extracted to: /tmp/tmpxyz/insights-archive-20250101-120000
🔍 Cloud metadata check:
  - AWS instance file: ❌
  - AWS metadata JSON: ❌
  - Overall status: ❌ MISSING
📁 Found PCP directory: /tmp/tmpxyz/insights-archive-20250101-120000/var/log/pcp/pmlogger
📁 Found metadata directory: /tmp/tmpxyz/insights-archive-20250101-120000/meta_data
🧹 Cleaned existing PCP files
🔧 Generating synthetic PCP archive: synthetic_pcp_idle
📊 Using pattern: idle - Very low utilization (~0.15% CPU, ~99.9% memory free)
📈 Expected synthetic metrics:
  - CPU usage: ~0.15%
  - Memory usage: ~0.1%
  - Detection: IDLE
  - Recommendation: Consider downsizing
✅ Synthetic PCP data generation successful!
🗜️ Compressing synthetic PCP files...
✅ Compressed: synthetic_pcp_idle.0 → synthetic_pcp_idle.0.xz
✅ Compressed: synthetic_pcp_idle.meta → synthetic_pcp_idle.meta.xz
📁 Synthetic PCP files in archive: ['synthetic_pcp_idle.0.xz', 'synthetic_pcp_idle.index', 'synthetic_pcp_idle.meta.xz']
📝 Updating PCP metadata: /tmp/tmpxyz/insights-archive-20250101-120000/meta_data/insights.specs.Specs.pcp_raw_data.json
✅ Updated metadata for 3 files
🔄 Cloud metadata missing - injecting synthetic metadata...
☁️ Injecting synthetic cloud metadata...
✅ Created synthetic AWS instance document: curl_-s_-H_X-aws-ec2-metadata-token_MockTokenABCD1234567890XYZsampleToken9876543210EFGH_http_..169.254.169.254.latest.dynamic.instance-identity.document_--connect-timeout_5
✅ Created synthetic cloud command file: cloud-init_query_-f_cloud_name_platform
✅ Created synthetic metadata JSON: insights.specs.Specs.aws_instance_id_doc.json
✅ Created synthetic metadata JSON: insights.specs.Specs.aws_instance_id_pkcs7.json
✅ Created synthetic metadata JSON: insights.specs.Specs.aws_public_hostnames.json
✅ Created synthetic metadata JSON: insights.specs.Specs.aws_public_ipv4_addresses.json
✅ Injected synthetic cloud metadata: 2 files + 4 JSON metadata
📊 Synthetic cloud instance details: t3.small in ap-northeast-1 (embedded)
📦 Creating synthetic Insights archive: idle_system.tar.gz
✅ Created synthetic archive: /home/user/idle_system.tar.gz

🎉 SUCCESS!
📁 Generated synthetic archive: /home/user/idle_system.tar.gz
📊 System State: idle
📈 Synthetic Metrics:
  - CPU utilization: ~0.15%
  - Memory utilization: ~0.1%
  - Expected detection: IDLE
  - Recommendation: Consider downsizing
☁️ Synthetic cloud metadata:
  - ✅ SELF-CONTAINED - No external dependencies!
  - ✅ Synthetic AWS metadata for testing
  - Instance type: t3.small
  - Region: ap-northeast-1
  - Perfect for development and testing environments!
```

## Workflow Overview

The tool performs the following workflow:

1. **📂 Extract Input Archive** - Decompress and extract the input Insights archive
2. **🔍 Check Existing Metadata** - Verify if cloud metadata already exists
3. **📁 Locate Directories** - Find PCP pmlogger and metadata directories
4. **🧹 Clean PCP Data** - Remove existing PCP files for replacement
5. **🔧 Generate Synthetic PCP** - Call native C binary to create performance data
6. **🗜️ Compress Files** - Compress PCP data files with xz
7. **📝 Update Metadata** - Update PCP metadata JSON files
8. **☁️ Inject Cloud Data** - Add synthetic AWS metadata if missing
9. **📦 Repackage Archive** - Create final synthetic Insights archive

## Embedded Cloud Metadata

The tool includes realistic synthetic AWS cloud metadata:

### Instance Information
- **Account ID**: `123456789012` (mock)
- **Instance ID**: `i-abcd1234567890xyz` (mock)
- **Instance Type**: `t3.small` (realistic)
- **AMI ID**: `ami-12345abcdef678901` (mock)
- **Region**: `ap-northeast-1` (realistic)
- **Availability Zone**: `ap-northeast-1c` (realistic)
- **Private IP**: `10.0.1.100` (mock)

### Metadata Files Created
- AWS instance identity document
- AWS metadata JSON specifications  
- Cloud platform detection files

## Integration

### With ROS Analysis Engine
```bash
# Generate test data for ROS recommendations
./synthetic-insights-generator.py baseline.tar.gz --pattern idle --output ros_idle_test
./synthetic-insights-generator.py baseline.tar.gz --pattern undersized --output ros_scaling_test

# Use generated archives with ROS engine
ros-engine analyze ros_idle_test.tar.gz
ros-engine analyze ros_scaling_test.tar.gz
```

### With PCP Analysis Tools
```bash
# Extract and analyze generated PCP data
tar -xf synthetic_archive.tar.gz
cd extracted_archive/var/log/pcp/pmlogger/

# Decompress PCP files
xz -d synthetic_pcp_idle.0.xz synthetic_pcp_idle.meta.xz

# Analyze with PCP tools
pminfo -a synthetic_pcp_idle
pmval -a synthetic_pcp_idle kernel.all.cpu.idle
pmdumptext -a synthetic_pcp_idle -t 5m
```

### Batch Processing
```bash
#!/bin/bash
# Generate all system states for testing

patterns=("idle" "optimized" "under_pressure" "undersized")
base_archive="baseline_archive.tar.gz"

for pattern in "${patterns[@]}"; do
    echo "Generating $pattern simulation..."
    ./synthetic-insights-generator.py "$base_archive" \
        --pattern "$pattern" \
        --output "test_${pattern}"
done

echo "Generated archives:"
ls -la test_*.tar.gz
```

## Troubleshooting

### Common Issues

#### 1. Missing PCP Binary
```bash
Error: Native C PMI program not found: ./synthetic-pcp-generator

# Solution: Compile the C binary
gcc -o synthetic-pcp-generator synthetic-pcp-generator.c -lpcp -lpcp_import

# Or specify different path
./synthetic-insights-generator.py input.tar.gz --pcp-generator-path /usr/bin/synthetic-pcp-generator
```

#### 2. Input Archive Not Found
```bash
Error: Input archive not found: missing_file.tar.gz

# Solution: Check file path and permissions
ls -la input_archive.tar.gz
```

#### 3. PCP Libraries Missing
```bash
# Install PCP development libraries
sudo dnf install pcp-devel pcp-import-devel  # Fedora/RHEL
sudo apt-get install libpcp3-dev libpcp-import1-dev  # Ubuntu
```

#### 4. Archive Corruption
```bash
# Test input archive integrity
tar -tzf input_archive.tar.gz > /dev/null

# Verify PCP data generation
./synthetic-pcp-generator test_output idle
ls -la test_output.*
```

#### 5. Permission Issues
```bash
# Make tools executable
chmod +x synthetic-insights-generator.py synthetic-pcp-generator

# Check directory permissions
ls -la ./
```

### Debug Mode
```bash
# Enable verbose output
./synthetic-insights-generator.py input.tar.gz --pattern idle 2>&1 | tee debug.log

# Check temporary files (tool cleans up automatically)
# If needed, manually inspect /tmp/tmp* directories during execution
```

## File Structure

### Input Requirements
- Insights archive (`.tar.gz`) with basic structure:
  - `data/` or `meta_data/` directory
  - `var/log/pcp/pmlogger/` directory (can be empty)

### Output Structure
```
synthetic_archive.tar.gz
└── insights-archive-timestamp/
    ├── data/
    │   └── insights_commands/
    │       ├── curl_-s_-H_X-aws-ec2-metadata-token_..._document_--connect-timeout_5
    │       └── cloud-init_query_-f_cloud_name_platform
    ├── meta_data/
    │   ├── insights.specs.Specs.aws_instance_id_doc.json
    │   ├── insights.specs.Specs.aws_instance_id_pkcs7.json
    │   ├── insights.specs.Specs.aws_public_hostnames.json
    │   ├── insights.specs.Specs.aws_public_ipv4_addresses.json
    │   └── insights.specs.Specs.pcp_raw_data.json
    └── var/
        └── log/
            └── pcp/
                └── pmlogger/
                    ├── synthetic_pcp_pattern.0.xz
                    ├── synthetic_pcp_pattern.index
                    └── synthetic_pcp_pattern.meta.xz
```

## Development

### Extending Patterns
To add new system patterns, modify both:
1. `synthetic-pcp-generator.c` - Add pattern definition
2. `synthetic-insights-generator.py` - Add pattern to `SYSTEM_PATTERNS` dict

### Custom Metadata
Modify the `AWS_METADATA_TEMPLATES` dictionary to change embedded cloud metadata.

### Testing
```bash
# Test all patterns
for pattern in idle optimized under_pressure undersized; do
    echo "Testing $pattern..."
    ./synthetic-insights-generator.py test_input.tar.gz --pattern "$pattern" --output "test_$pattern"
done
```

## Files

- `synthetic-insights-generator.py` - Main Python orchestrator
- `synthetic-pcp-generator` - Native C binary dependency  
- `README_synthetic-insights-generator.md` - This documentation

## Related Tools

- **synthetic-pcp-generator** - Native C binary for PCP data generation ([Source Code](https://github.com/upadhyeammit/synthetic-pcp-generator))
- **ROS Engine** - Consumes generated archives for optimization recommendations
- **PCP Tools** - `pminfo`, `pmval`, `pmdumptext` for data analysis

## License

This tool is part of the ROS (Resource Optimization Service) project.

---