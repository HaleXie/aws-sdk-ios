#!/usr/bin/env python3

import os
import hashlib
import re
from pathlib import Path

def calculate_sha256(file_path):
    """Calculate SHA256 checksum for a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def update_package_swift(checksums, package_swift_path):
    """Update the frameworksToChecksum dictionary in Package.swift"""
    print(f"📝 Updating {package_swift_path}...")
    
    # Read the current Package.swift file
    with open(package_swift_path, 'r') as f:
        content = f.read()
    
    # Generate the new frameworksToChecksum dictionary
    checksum_lines = []
    for framework_name in sorted(checksums.keys()):
        checksum = checksums[framework_name]
        checksum_lines.append(f'    "{framework_name}": "{checksum}",')
    
    new_checksum_dict = "let frameworksToChecksum = [\n" + "\n".join(checksum_lines) + "\n]"
    
    # Use regex to replace the existing frameworksToChecksum dictionary
    pattern = r'let frameworksToChecksum = \[[\s\S]*?\]'
    
    if re.search(pattern, content):
        updated_content = re.sub(pattern, new_checksum_dict, content)
        
        # Write the updated content back to the file
        with open(package_swift_path, 'w') as f:
            f.write(updated_content)
        
        print(f"   ✅ Successfully updated frameworksToChecksum dictionary")
        return True
    else:
        print(f"   ❌ Could not find frameworksToChecksum dictionary in Package.swift")
        return False

def main():
    print("🔐 Generating SHA256 checksums and updating Package.swift")
    print("=" * 70)
    
    # Set up paths
    project_root = Path("/Volumes/WorkData/Workspace/hl/aws-sdk-ios")
    zip_dir = project_root / "xcframeworks" / "output" / "zips"
    package_swift_path = project_root / "Package.swift"
    
    if not zip_dir.exists():
        print("❌ ZIP directory not found:", zip_dir)
        return
    
    if not package_swift_path.exists():
        print("❌ Package.swift not found:", package_swift_path)
        return
    
    # Find all ZIP files
    zip_files = list(zip_dir.glob("*-2.41.0-visionOS.zip"))
    
    if not zip_files:
        print("❌ No ZIP files found in", zip_dir)
        return
    
    print(f"📁 Found {len(zip_files)} ZIP files")
    print("")
    
    # Calculate checksums
    checksums = {}
    
    for zip_file in sorted(zip_files):
        # Extract framework name from ZIP filename
        framework_name = zip_file.stem.replace("-2.41.0-visionOS", "")
        
        print(f"🔍 Calculating checksum for {framework_name}...")
        checksum = calculate_sha256(zip_file)
        checksums[framework_name] = checksum
        
        size_mb = zip_file.stat().st_size / (1024 * 1024)
        print(f"   ✅ {checksum[:16]}... ({size_mb:.1f} MB)")
    
    print("")
    print("=" * 70)
    
    # Update Package.swift
    success = update_package_swift(checksums, package_swift_path)
    
    if success:
        print("")
        print("✅ PACKAGE.SWIFT UPDATE COMPLETE")
        print("=" * 70)
        print(f"📊 Updated checksums for {len(checksums)} frameworks")
        print(f"📁 ZIP files location: {zip_dir}")
        print(f"📝 Package.swift updated: {package_swift_path}")
        print("")
        print("🎯 All frameworks now have updated SHA256 checksums for version 2.41.0-visionOS")
    else:
        print("")
        print("❌ PACKAGE.SWIFT UPDATE FAILED")
        print("=" * 70)
        print("Manual update required. Use the following checksums:")
        print("")
        print("let frameworksToChecksum = [")
        for framework_name in sorted(checksums.keys()):
            checksum = checksums[framework_name]
            print(f'    "{framework_name}": "{checksum}",')
        print("]")
    
    print("=" * 70)

if __name__ == "__main__":
    main()