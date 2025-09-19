#!/usr/bin/env python3
"""
Synthetic Insights Generator - Create realistic Insights archives with native PCP data
Complete self-contained solution supporting ALL system states: idle, optimized, under_pressure, undersized
Generates synthetic performance data with embedded cloud metadata for testing and development.
"""

import os
import sys
import tempfile
import shutil
import tarfile
import subprocess
import json
import argparse


class SyntheticInsightsGenerator:
    """Generate synthetic Insights archives with realistic PCP data and cloud metadata for all system states."""

    # EMBEDDED AWS CLOUD METADATA - No external dependencies needed
    AWS_INSTANCE_DOCUMENT = """{
  "accountId" : "123456789012",
  "architecture" : "x86_64",
  "availabilityZone" : "ap-northeast-1c",
  "billingProducts" : [ "bp-mock12345" ],
  "devpayProductCodes" : null,
  "marketplaceProductCodes" : null,
  "imageId" : "ami-12345abcdef678901",
  "instanceId" : "i-abcd1234567890xyz",
  "instanceType" : "t3.small",
  "kernelId" : null,
  "pendingTime" : "2024-01-01T12:00:00Z",
  "privateIp" : "10.0.1.100",
  "ramdiskId" : null,
  "region" : "ap-northeast-1",
  "version" : "2017-09-30"
}"""

    # AWS Metadata JSON Templates
    AWS_METADATA_TEMPLATES = {
        "insights.specs.Specs.aws_instance_id_doc.json": {
            "name": "insights.specs.Specs.aws_instance_id_doc",
            "exec_time": 0.0002298355102539,
            "errors": [],
            "results": {
                "type": "insights.core.spec_factory.CommandOutputProvider",
                "object": {
                    "rc": None,
                    "cmd": "/usr/bin/curl -s -H \"X-aws-ec2-metadata-token: "
                           "MockTokenABCD1234567890XYZsampleToken9876543210EFGH==\" "
                           "http://169.254.169.254/latest/dynamic/instance-identity/document --connect-timeout 5",
                    "args": None,
                    "save_as": False,
                    "relative_path": "insights_commands/curl_-s_-H_X-aws-ec2-metadata-token_"
                                     "MockTokenABCD1234567890XYZsampleToken9876543210EFGH_http_.."
                                     "169.254.169.254.latest.dynamic.instance-identity.document_--connect-timeout_5"
                }
            },
            "ser_time": 0.016474246978759766
        },
        "insights.specs.Specs.aws_instance_id_pkcs7.json": {
            "name": "insights.specs.Specs.aws_instance_id_pkcs7",
            "exec_time": 0.0002226829528808594,
            "errors": [],
            "results": {
                "type": "insights.core.spec_factory.CommandOutputProvider",
                "object": {
                    "rc": None,
                    "cmd": "/usr/bin/curl -s -H \"X-aws-ec2-metadata-token: "
                           "MockTokenABCD1234567890XYZsampleToken9876543210EFGH==\" "
                           "http://169.254.169.254/latest/dynamic/instance-identity/pkcs7 --connect-timeout 5",
                    "args": None,
                    "save_as": False,
                    "relative_path": "insights_commands/curl_-s_-H_X-aws-ec2-metadata-token_"
                                     "MockTokenABCD1234567890XYZsampleToken9876543210EFGH_http_.."
                                     "169.254.169.254.latest.dynamic.instance-identity.pkcs7_--connect-timeout_5"
                }
            },
            "ser_time": 0.016751527786254883
        },
        "insights.specs.Specs.aws_public_hostnames.json": {
            "name": "insights.specs.Specs.aws_public_hostnames",
            "exec_time": 0.00030684471130371094,
            "errors": [],
            "results": {
                "type": "insights.core.spec_factory.CommandOutputProvider",
                "object": {
                    "rc": None,
                    "cmd": "/usr/bin/curl -s -H \"X-aws-ec2-metadata-token: "
                           "MockTokenABCD1234567890XYZsampleToken9876543210EFGH==\" "
                           "http://169.254.169.254/latest/meta-data/public-hostname --connect-timeout 5",
                    "args": None,
                    "save_as": False,
                    "relative_path": "insights_commands/curl_-s_-H_X-aws-ec2-metadata-token_"
                                     "MockTokenABCD1234567890XYZsampleToken9876543210EFGH_http_.."
                                     "169.254.169.254.latest.meta-data.public-hostname_--connect-timeout_5"
                }
            },
            "ser_time": 0.021778106689453125
        },
        "insights.specs.Specs.aws_public_ipv4_addresses.json": {
            "name": "insights.specs.Specs.aws_public_ipv4_addresses",
            "exec_time": 0.00025,
            "errors": [],
            "results": {
                "type": "insights.core.spec_factory.CommandOutputProvider",
                "object": {
                    "rc": None,
                    "cmd": "/usr/bin/curl -s -H \"X-aws-ec2-metadata-token: "
                           "MockTokenABCD1234567890XYZsampleToken9876543210EFGH==\" "
                           "http://169.254.169.254/latest/meta-data/public-ipv4 --connect-timeout 5",
                    "args": None,
                    "save_as": False,
                    "relative_path": "insights_commands/curl_-s_-H_X-aws-ec2-metadata-token_"
                                     "MockTokenABCD1234567890XYZsampleToken9876543210EFGH_http_.."
                                     "169.254.169.254.latest.meta-data.public-ipv4_--connect-timeout_5"
                }
            },
            "ser_time": 0.021
        }
    }

    # Cloud-related insights command files content
    CLOUD_COMMANDS = {
        "cloud-init_query_-f_cloud_name_platform": "aws\nec2",
    }

    # System state patterns based on POC metrics
    SYSTEM_PATTERNS = {
        'idle': {
            'description': 'Very low utilization (~0.15% CPU, ~99.9% memory free)',
            'cpu_usage_percent': 0.15,
            'memory_usage_percent': 0.1,
            'detection': 'IDLE',
            'recommendation': 'Consider downsizing'
        },
        'optimized': {
            'description': 'Balanced utilization (~50% CPU, ~63.6% memory free)',
            'cpu_usage_percent': 50.0,
            'memory_usage_percent': 36.4,
            'detection': 'OPTIMIZED',
            'recommendation': 'Well balanced system'
        },
        'under_pressure': {
            'description': 'Moderate utilization with high pressure',
            'cpu_usage_percent': 10.0,
            'memory_usage_percent': 12.2,
            'detection': 'UNDER_PRESSURE',
            'recommendation': 'Check pressure sources'
        },
        'undersized': {
            'description': 'High utilization (~90% CPU, ~96.9% memory usage)',
            'cpu_usage_percent': 90.0,
            'memory_usage_percent': 96.9,
            'detection': 'UNDERSIZED',
            'recommendation': 'Scale up recommended'
        }
    }

    def __init__(self, c_program_path=None):
        if c_program_path is None:
            # Default to current directory for synthetic-pcp-generator binary
            c_program_path = "./synthetic-pcp-generator"

        self.c_program = c_program_path
        if not os.path.exists(self.c_program):
            raise FileNotFoundError(f"Native C PMI program not found: {self.c_program}")

        print(f"✅ Native C PMI program ready: {self.c_program}")
        print("✅ Cloud metadata: Embedded in script (self-contained)")
        print(f"✅ Supported patterns: {', '.join(self.SYSTEM_PATTERNS.keys())}")

    def extract_insights_archive(self, archive_path, extract_dir):
        """Extract Insights archive (handles both .tar.gz and .tar)."""
        print(f"📂 Extracting Insights archive: {archive_path}")

        # Try different extraction modes
        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
        except Exception:
            # Try as plain tar
            with tarfile.open(archive_path, 'r:') as tar:
                tar.extractall(extract_dir)

        # Find the main directory (usually has a timestamp)
        extracted_items = os.listdir(extract_dir)
        main_dir = None

        for item in extracted_items:
            item_path = os.path.join(extract_dir, item)
            if os.path.isdir(item_path):
                main_dir = item_path
                break

        if not main_dir:
            raise RuntimeError("Could not find main directory in extracted archive")

        print(f"✅ Extracted to: {main_dir}")
        return main_dir

    def find_pcp_directory(self, main_dir):
        """Find the PCP pmlogger directory."""
        possible_paths = [
            os.path.join(main_dir, "data", "var", "log", "pcp", "pmlogger"),
            os.path.join(main_dir, "var", "log", "pcp", "pmlogger")
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"📁 Found PCP directory: {path}")
                return path

        raise RuntimeError("Could not find PCP pmlogger directory")

    def find_metadata_directory(self, main_dir):
        """Find the metadata directory."""
        possible_paths = [
            os.path.join(main_dir, "meta_data"),
            os.path.join(main_dir, "metadata")
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"📁 Found metadata directory: {path}")
                return path

        raise RuntimeError("Could not find metadata directory")

    def check_cloud_metadata_exists(self, main_dir):
        """Check if cloud metadata already exists in the archive."""
        try:
            metadata_dir = self.find_metadata_directory(main_dir)
            insights_commands_dir = os.path.join(main_dir, "data", "insights_commands")

            # Check for AWS instance identity document file
            aws_instance_file_found = False
            if os.path.exists(insights_commands_dir):
                for file in os.listdir(insights_commands_dir):
                    if "instance-identity.document" in file and "curl" in file:
                        aws_instance_file_found = True
                        break

            # Check for AWS metadata JSON
            aws_metadata_json = os.path.join(metadata_dir, "insights.specs.Specs.aws_instance_id_doc.json")
            aws_json_exists = os.path.exists(aws_metadata_json)

            cloud_exists = aws_instance_file_found and aws_json_exists

            print("🔍 Cloud metadata check:")
            print(f"  - AWS instance file: {'✅' if aws_instance_file_found else '❌'}")
            print(f"  - AWS metadata JSON: {'✅' if aws_json_exists else '❌'}")
            print(f"  - Overall status: {'✅ EXISTS' if cloud_exists else '❌ MISSING'}")

            return cloud_exists

        except Exception as e:
            print(f"⚠️ Error checking cloud metadata: {e}")
            return False

    def generate_native_pcp_archive(self, output_base_name, pattern_type, work_dir):
        """Generate PCP archive using native C PMI with specified pattern."""
        original_dir = os.getcwd()

        try:
            os.chdir(work_dir)

            c_pattern = pattern_type

            pattern_info = self.SYSTEM_PATTERNS.get(pattern_type, {})

            print(f"🔧 Generating synthetic PCP archive: {output_base_name}")
            print(f"📊 Using pattern: {pattern_type} - {pattern_info.get('description', 'Unknown pattern')}")
            print("📈 Expected synthetic metrics:")
            print(f"  - CPU usage: ~{pattern_info.get('cpu_usage_percent', 'N/A')}%")
            print(f"  - Memory usage: ~{pattern_info.get('memory_usage_percent', 'N/A')}%")
            print(f"  - Detection: {pattern_info.get('detection', 'Unknown')}")
            print(f"  - Recommendation: {pattern_info.get('recommendation', 'Unknown')}")

            # Clean up any existing files
            for ext in ['0', 'index', 'meta', '0.xz', 'meta.xz']:
                file_path = f"{output_base_name}.{ext}"
                if os.path.exists(file_path):
                    os.remove(file_path)

            # Run native C PMI program with pattern
            result = subprocess.run([self.c_program, output_base_name, c_pattern],
                                    capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                raise RuntimeError(f"Native C PMI failed: {result.stderr}")

            print("✅ Synthetic PCP data generation successful!")

            # Verify files were created
            required_files = [f"{output_base_name}.{ext}" for ext in ['0', 'index', 'meta']]
            for file in required_files:
                if not os.path.exists(file):
                    raise FileNotFoundError(f"Expected file not created: {file}")

            return required_files

        finally:
            os.chdir(original_dir)

    def compress_pcp_files(self, base_name, work_dir):
        """Compress .0 and .meta files with xz."""
        original_dir = os.getcwd()

        try:
            os.chdir(work_dir)

            print("🗜️ Compressing synthetic PCP files...")

            # Compress .0 and .meta files
            for ext in ['0', 'meta']:
                file_path = f"{base_name}.{ext}"
                if os.path.exists(file_path):
                    result = subprocess.run(['xz', file_path],
                                            capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✅ Compressed: {file_path} → {file_path}.xz")
                    else:
                        raise RuntimeError(f"Failed to compress {file_path}: {result.stderr}")

            # Return final file list
            return [f"{base_name}.{ext}" for ext in ['0.xz', 'index', 'meta.xz']]

        finally:
            os.chdir(original_dir)

    def update_pcp_metadata_json(self, metadata_dir, archive_name):
        """Update insights.specs.Specs.pcp_raw_data.json with new archive files."""
        json_file = os.path.join(metadata_dir, "insights.specs.Specs.pcp_raw_data.json")

        if not os.path.exists(json_file):
            print(f"⚠️ PCP metadata JSON not found: {json_file}")
            return

        print(f"📝 Updating PCP metadata: {json_file}")

        # Expected files for our archive
        expected_files = [
            f"var/log/pcp/pmlogger/{archive_name}.0.xz",
            f"var/log/pcp/pmlogger/{archive_name}.index",
            f"var/log/pcp/pmlogger/{archive_name}.meta.xz"
        ]

        # Create new results list
        new_results = []
        for file_path in expected_files:
            new_results.append({
                "type": "insights.core.spec_factory.RawFileProvider",
                "object": {
                    "save_as": True,
                    "relative_path": file_path,
                    "rc": None
                }
            })

        # Update JSON
        with open(json_file, 'r') as f:
            data = json.load(f)

        data["results"] = new_results

        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Updated metadata for {len(expected_files)} files")

    def inject_embedded_cloud_metadata(self, target_main_dir):
        """Inject synthetic cloud metadata using embedded data (no external dependencies)."""
        print("☁️ Injecting synthetic cloud metadata...")

        target_insights_commands = os.path.join(target_main_dir, "data", "insights_commands")
        target_metadata_dir = self.find_metadata_directory(target_main_dir)

        # Ensure target directory exists
        os.makedirs(target_insights_commands, exist_ok=True)

        cloud_files_created = 0

        # Create AWS instance identity document file
        aws_document_filename = (
            "curl_-s_-H_X-aws-ec2-metadata-token_MockTokenABCD1234567890XYZsampleToken9876543210EFGH_"
            "http_..169.254.169.254.latest.dynamic.instance-identity.document_--connect-timeout_5"
        )
        aws_document_path = os.path.join(target_insights_commands, aws_document_filename)

        with open(aws_document_path, 'w') as f:
            f.write(self.AWS_INSTANCE_DOCUMENT)
        print(f"✅ Created synthetic AWS instance document: {aws_document_filename}")
        cloud_files_created += 1

        # Create other cloud command files
        for filename, content in self.CLOUD_COMMANDS.items():
            file_path = os.path.join(target_insights_commands, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Created synthetic cloud command file: {filename}")
            cloud_files_created += 1

        # Create AWS metadata JSON files
        metadata_files_created = 0
        for filename, template in self.AWS_METADATA_TEMPLATES.items():
            json_path = os.path.join(target_metadata_dir, filename)
            with open(json_path, 'w') as f:
                json.dump(template, f, indent=2)
            print(f"✅ Created synthetic metadata JSON: {filename}")
            metadata_files_created += 1

        print(f"✅ Injected synthetic cloud metadata: {cloud_files_created} files + "
              f"{metadata_files_created} JSON metadata")
        print("📊 Synthetic cloud instance details: t3.small in ap-northeast-1 (embedded)")

    def create_insights_archive(self, main_dir, output_name):
        """Create final .tar.gz synthetic Insights archive."""
        archive_name = f"{output_name}.tar.gz"

        print(f"📦 Creating synthetic Insights archive: {archive_name}")

        # Get the base directory name
        base_name = os.path.basename(main_dir)
        parent_dir = os.path.dirname(main_dir)

        original_dir = os.getcwd()

        try:
            os.chdir(parent_dir)

            with tarfile.open(archive_name, 'w:gz') as tar:
                tar.add(base_name)

            final_path = os.path.join(original_dir, archive_name)
            shutil.move(archive_name, final_path)

            print(f"✅ Created synthetic archive: {final_path}")
            return final_path

        finally:
            os.chdir(original_dir)

    def process_insights_archive(self, input_archive, pattern_type="undersized", output_name=None):
        """
        Complete workflow: Extract → Generate Synthetic PCP → Check/Inject Synthetic Cloud Data
        → Update Metadata → Repackage
        """
        if pattern_type not in self.SYSTEM_PATTERNS:
            raise ValueError(f"Unknown pattern '{pattern_type}'. Supported: {', '.join(self.SYSTEM_PATTERNS.keys())}")

        if output_name is None:
            base = os.path.splitext(os.path.basename(input_archive))[0]
            output_name = f"synthetic_{pattern_type}_{base}"

        pattern_info = self.SYSTEM_PATTERNS[pattern_type]

        print("🚀 Processing Insights archive with Synthetic PCP Data + Embedded Cloud Metadata")
        print(f"📂 Input: {input_archive}")
        print(f"📊 Pattern: {pattern_type} - {pattern_info['description']}")
        print("☁️ Cloud: Synthetic metadata (self-contained)")
        print(f"📂 Output: {output_name}")
        print("")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract archive
            main_dir = self.extract_insights_archive(input_archive, temp_dir)

            # Check if cloud metadata exists
            cloud_exists = self.check_cloud_metadata_exists(main_dir)

            # Find directories
            pcp_dir = self.find_pcp_directory(main_dir)
            metadata_dir = self.find_metadata_directory(main_dir)

            # Clean existing PCP files
            for file in os.listdir(pcp_dir):
                file_path = os.path.join(pcp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print("🧹 Cleaned existing PCP files")

            # Generate new archive name based on pattern
            archive_base_name = f"synthetic_pcp_{pattern_type}"

            # Generate synthetic PCP archive
            self.generate_native_pcp_archive(archive_base_name, pattern_type, pcp_dir)

            # Compress files
            compressed_files = self.compress_pcp_files(archive_base_name, pcp_dir)

            # Verify compressed files exist
            for file in compressed_files:
                file_path = os.path.join(pcp_dir, file)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Compressed file missing: {file_path}")

            print(f"📁 Synthetic PCP files in archive: {compressed_files}")

            # Update PCP metadata
            self.update_pcp_metadata_json(metadata_dir, archive_base_name)

            # Inject synthetic cloud metadata if missing
            if not cloud_exists:
                print("🔄 Cloud metadata missing - injecting synthetic metadata...")
                self.inject_embedded_cloud_metadata(main_dir)
            else:
                print("✅ Cloud metadata already exists - no injection needed")

            # Create final archive
            final_archive = self.create_insights_archive(main_dir, output_name)

            return final_archive


def main():
    parser = argparse.ArgumentParser(
        description='Synthetic Insights Generator - Create realistic test archives with '
                    'embedded cloud metadata and native PCP data'
    )
    parser.add_argument('input_archive', nargs='?', help='Input Insights .tar.gz archive')
    parser.add_argument('--pattern', default='undersized',
                        choices=['idle', 'optimized', 'under_pressure', 'undersized'],
                        help='System state pattern to generate')
    parser.add_argument('--output', help='Output archive name (without .tar.gz)')
    parser.add_argument('--pcp-generator-path', default=None,
                        help='Path to synthetic-pcp-generator binary (default: ./synthetic-pcp-generator)')
    parser.add_argument('--list-patterns', action='store_true', help='List all available patterns')

    args = parser.parse_args()

    if args.list_patterns:
        print("📊 Synthetic Insights Generator - Available System State Patterns:")
        generator = SyntheticInsightsGenerator(args.pcp_generator_path)
        for pattern, info in generator.SYSTEM_PATTERNS.items():
            print(f"  {pattern:15} - {info['description']}")
            print(f"                    CPU: ~{info['cpu_usage_percent']}%, Memory: ~{info['memory_usage_percent']}%")
            print(f"                    Detection: {info['detection']}, {info['recommendation']}")
            print()
        return

    if not args.input_archive:
        print("❌ Input archive is required when not using --list-patterns")
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.input_archive):
        print(f"❌ Input archive not found: {args.input_archive}")
        sys.exit(1)

    try:
        generator = SyntheticInsightsGenerator(args.pcp_generator_path)
        result = generator.process_insights_archive(
            args.input_archive,
            args.pattern,
            args.output
        )

        pattern_info = generator.SYSTEM_PATTERNS[args.pattern]

        print("\n🎉 SUCCESS!")
        print(f"📁 Generated synthetic archive: {result}")
        print(f"📊 System State: {args.pattern}")
        print("📈 Synthetic Metrics:")
        print(f"  - CPU utilization: ~{pattern_info['cpu_usage_percent']}%")
        print(f"  - Memory utilization: ~{pattern_info['memory_usage_percent']}%")
        print(f"  - Expected detection: {pattern_info['detection']}")
        print(f"  - Recommendation: {pattern_info['recommendation']}")
        print("☁️ Synthetic cloud metadata:")
        print("  - ✅ SELF-CONTAINED - No external dependencies!")
        print("  - ✅ Synthetic AWS metadata for testing")
        print("  - Instance type: t3.small")
        print("  - Region: ap-northeast-1")
        print("  - Perfect for development and testing environments!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
