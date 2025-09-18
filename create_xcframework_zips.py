#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

# Extract version from Package.swift (same as used in the Package.swift file)
LATEST_VERSION = "2.41.0-visionOS"

def run_command(cmd, cwd=None):
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def create_xcframework_zip(xcframework_path, output_dir):
    """Create a zip file for an XCFramework"""
    xcframework_name = xcframework_path.stem
    zip_name = f"{xcframework_name}-{LATEST_VERSION}.zip"
    zip_path = output_dir / zip_name
    
    print(f"📦 Creating {zip_name}...")
    
    # Use zip command to create the archive
    cmd = [
        "zip", 
        "-r", 
        str(zip_path),
        xcframework_path.name
    ]
    
    exit_code, stdout, stderr = run_command(cmd, cwd=xcframework_path.parent)
    
    if exit_code == 0:
        # Get file size for reporting
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Created {zip_name} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"   ❌ Failed to create {zip_name}")
        print(f"      Error: {stderr}")
        return False

def main():
    print("📦 Creating ZIP files for AWS iOS SDK XCFrameworks")
    print("=" * 60)
    print(f"🏷️  Version: {LATEST_VERSION}")
    
    # Set up paths
    project_root = Path("/Volumes/WorkData/Workspace/hl/aws-sdk-ios")
    xcf_dir = project_root / "xcframeworks" / "output" / "XCF"
    zip_output_dir = project_root / "xcframeworks" / "output" / "zips"
    
    # Create output directory for zips
    zip_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all XCFrameworks
    xcframeworks = list(xcf_dir.glob("*.xcframework"))
    
    if not xcframeworks:
        print("❌ No XCFrameworks found in xcframeworks/output/XCF/")
        sys.exit(1)
    
    print(f"📁 Found {len(xcframeworks)} XCFrameworks to zip")
    print("")
    
    # Create zip for each XCFramework
    successful_zips = 0
    failed_zips = 0
    
    for xcframework in sorted(xcframeworks):
        success = create_xcframework_zip(xcframework, zip_output_dir)
        if success:
            successful_zips += 1
        else:
            failed_zips += 1
    
    # Summary
    print("")
    print("=" * 60)
    print("📊 ZIP CREATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully created: {successful_zips} zip files")
    print(f"❌ Failed to create: {failed_zips} zip files")
    print(f"📁 Output directory: {zip_output_dir}")
    
    if successful_zips > 0:
        print("")
        print("📦 Generated ZIP files:")
        zip_files = list(zip_output_dir.glob("*.zip"))
        for zip_file in sorted(zip_files):
            size_mb = zip_file.stat().st_size / (1024 * 1024)
            print(f"   • {zip_file.name} ({size_mb:.1f} MB)")
    
    print("")
    print("🎯 These ZIP files follow the Package.swift naming convention:")
    print(f"   Format: <framework>-{LATEST_VERSION}.zip")
    print("=" * 60)

if __name__ == "__main__":
    main()

