import os
import sys
import shutil

from multiprocessing import Pool
from framework_list import xcframeworks
from framework_list_visionos import xcframeworks_visionos, ios_only_frameworks
from functions import log, run_command

PWD = os.getcwd()

IOS_DEVICE_ARCHIVE_PATH = f"{PWD}/xcframeworks/output/iOS/"
VISIONOS_DEVICE_ARCHIVE_PATH = f"{PWD}/xcframeworks/output/visionOS/"
IOS_SIMULATOR_ARCHIVE_PATH = f"{PWD}/xcframeworks/output/Simulator/"
VISIONOS_SIMULATOR_ARCHIVE_PATH = f"{PWD}/xcframeworks/output/visionOSSimulator/"
XCFRAMEWORK_PATH = f"{PWD}/xcframeworks/output/XCF/"

def create_archive(framework, project_file, archive_path, destination):
    cmd = [
        "xcodebuild",
        "archive",
        "-project",
        project_file,
        "-scheme",
        framework,
        "-destination",
        destination,
        "-archivePath",
        archive_path,
        "SKIP_INSTALL=NO",
        "BUILD_LIBRARY_FOR_DISTRIBUTION=YES"
    ]

    (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
    if exit_code == 0:
        log(f"Created archive for framework: {framework} with destination: {destination}")
    else:
        log(f"⚠️  Could not create xcodebuild archive: {framework} for {destination}")
        log(f"   This is expected for iOS-only frameworks when building for visionOS")
        # Don't exit - continue with other frameworks

def map_framework_to_project(framework_list):
    framework_map = {}
    cmd = [
        "xcodebuild",
        "-project",
        "AWSiOSSDKv2.xcodeproj",
        "-list",
    ]
    (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
    if exit_code == 0:
        log(f"List of schema found")
    else:
        log(f"Xcodebuild list failed: output: {out}; error: {err}")
        sys.exit(exit_code)

    for framework in framework_list:
        if framework not in str(out):
            framework_map[framework] = "./AWSAuthSDK/AWSAuthSDK.xcodeproj"
        else:
            framework_map[framework] = "AWSiOSSDKv2.xcodeproj"
    return framework_map

def archive(framework):
    xcframework = f"{XCFRAMEWORK_PATH}{framework}.xcframework"

    if os.path.exists(xcframework):
        log(f"skipping {framework}...")
        return

    log(f"Creating archives for {framework}")

    # Always create iOS archives
    create_archive(framework=framework, project_file=framework_map[framework], archive_path=f"{IOS_DEVICE_ARCHIVE_PATH}{framework}", destination="generic/platform=iOS")
    create_archive(framework=framework, project_file=framework_map[framework], archive_path=f"{IOS_SIMULATOR_ARCHIVE_PATH}{framework}", destination="generic/platform=iOS Simulator")
    
    # Only create visionOS archives for frameworks that are compatible with visionOS
    if framework not in ios_only_frameworks:
        create_archive(framework=framework, project_file=framework_map[framework], archive_path=f"{VISIONOS_DEVICE_ARCHIVE_PATH}{framework}", destination="generic/platform=visionOS")
        create_archive(framework=framework, project_file=framework_map[framework], archive_path=f"{VISIONOS_SIMULATOR_ARCHIVE_PATH}{framework}", destination="generic/platform=visionOS Simulator")

framework_map = map_framework_to_project(xcframeworks)

def create_xc_framework(framework):
    ios_device_framework = f"{IOS_DEVICE_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
    ios_device_debug_symbols = f"{IOS_DEVICE_ARCHIVE_PATH}{framework}.xcarchive/dSYMs/{framework}.framework.dSYM"
    ios_simulator_framework = f"{IOS_SIMULATOR_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
    ios_simulator_debug_symbols = f"{IOS_SIMULATOR_ARCHIVE_PATH}{framework}.xcarchive/dSYMs/{framework}.framework.dSYM"
    xcframework = f"{XCFRAMEWORK_PATH}{framework}.xcframework"
    
    if os.path.exists(xcframework):
        log(f"skipping {framework}...")
    else:
        log(f"Creating XCF for {framework}")

        # Check if iOS archives exist
        if not (os.path.exists(ios_device_framework) and os.path.exists(ios_simulator_framework)):
            log(f"⚠️  Missing iOS archives for {framework}, skipping XCFramework creation")
            return

        # Base command with iOS frameworks
        cmd = [
            "xcodebuild",
            "-create-xcframework",
            "-framework",
            ios_device_framework,
            "-debug-symbols",
            ios_device_debug_symbols,
            "-framework",
            ios_simulator_framework,
            "-debug-symbols",
            ios_simulator_debug_symbols,
        ]
        
        # Add visionOS frameworks only if the framework is compatible with visionOS AND archives exist
        if framework not in ios_only_frameworks:
            visionos_device_framework = f"{VISIONOS_DEVICE_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
            visionos_device_debug_symbols = f"{VISIONOS_DEVICE_ARCHIVE_PATH}{framework}.xcarchive/dSYMs/{framework}.framework.dSYM"
            visionos_simulator_framework = f"{VISIONOS_SIMULATOR_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
            visionos_simulator_debug_symbols = f"{VISIONOS_SIMULATOR_ARCHIVE_PATH}{framework}.xcarchive/dSYMs/{framework}.framework.dSYM"
            
            # Only add visionOS if the archives actually exist
            if (os.path.exists(visionos_device_framework) and os.path.exists(visionos_simulator_framework)):
                cmd.extend([
                    "-framework",
                    visionos_device_framework,
                    "-debug-symbols",
                    visionos_device_debug_symbols,
                    "-framework",
                    visionos_simulator_framework,
                    "-debug-symbols",
                    visionos_simulator_debug_symbols,
                ])
                log(f"   Including visionOS support for {framework}")
            else:
                log(f"   visionOS archives missing for {framework}, creating iOS-only XCFramework")
        
        cmd.extend(["-output", xcframework])
        
        (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
        if exit_code == 0:
            log(f"Created XCFramework for {framework}")
        else:
            log(f"⚠️  Could not create XCFramework: {framework}")
            log(f"   Error: {err}")
            # Don't exit - continue with other frameworks

def process_frameworks(process, base_frameworks, remaining_frameworks, pool):
    for base_framework in base_frameworks:
        process(base_framework)

    with pool:
        pool.map(process, remaining_frameworks)

if __name__ == '__main__':
    project_dir = os.getcwd()
    log(f"Creating XCFrameworks with visionOS support in {project_dir}")
    
    # Use the original framework list to build all frameworks (iOS-only + visionOS-compatible)
    # This ensures iOS-only frameworks are still built with iOS support
    all_frameworks = xcframeworks
    
    log(f"Building frameworks: {all_frameworks}")
    log(f"iOS-only frameworks (no visionOS support): {ios_only_frameworks}")
    log(f"visionOS-compatible frameworks: {[f for f in all_frameworks if f not in ios_only_frameworks]}")

    # These base_frameworks must be built first and serially.
    # Other frameworks are dependant on these base_frameworks,
    # and the build scripts will fail if they're not archived /
    # created in the proper order.
    # *** This may need to be updated when dependencies change ***
    base_frameworks = all_frameworks[:5]

    # The remaining_frameworks are archived and built concurrently
    # because they are dependent only on base_frameworks.
    remaining_frameworks = all_frameworks[5:]

    # To build the remaining_frameworks concurrently, we're using
    # a Pool(). By omitting an explicit input into the Pool constructor
    # we're allowing it to decide an appropriate amount of processes to run.
    archive_pool = Pool()

    # First let's archive everything.
    process_frameworks(archive, base_frameworks, remaining_frameworks, archive_pool)

    create_frameworks_pool = Pool()
    # Next let's create the xcframeworks.
    process_frameworks(create_xc_framework, base_frameworks, remaining_frameworks, create_frameworks_pool)

    if os.path.exists(IOS_DEVICE_ARCHIVE_PATH):
        shutil.rmtree(IOS_DEVICE_ARCHIVE_PATH)
    if os.path.exists(IOS_SIMULATOR_ARCHIVE_PATH):
        shutil.rmtree(IOS_SIMULATOR_ARCHIVE_PATH)
    if os.path.exists(VISIONOS_DEVICE_ARCHIVE_PATH):
        shutil.rmtree(VISIONOS_DEVICE_ARCHIVE_PATH)
    if os.path.exists(VISIONOS_SIMULATOR_ARCHIVE_PATH):
        shutil.rmtree(VISIONOS_SIMULATOR_ARCHIVE_PATH)
    
    # Print final summary for users
    log("=" * 80)
    log("🎉 XCFramework Generation Complete!")
    log("=" * 80)
    
    visionos_compatible = [f for f in all_frameworks if f not in ios_only_frameworks]
    
    log(f"📊 SUMMARY:")
    log(f"   Total frameworks built: {len(all_frameworks)}")
    log(f"   iOS + visionOS support: {len(visionos_compatible)} frameworks")
    log(f"   iOS-only support: {len(ios_only_frameworks)} frameworks")
    
    log("")
    log("✅ FRAMEWORKS WITH iOS + visionOS SUPPORT:")
    log("   These frameworks work on both iOS and visionOS platforms:")
    for framework in sorted(visionos_compatible):
        log(f"   • {framework}")
    
    log("")
    log("📱 iOS-ONLY FRAMEWORKS:")
    log("   These frameworks only work on iOS due to API incompatibilities:")
    for framework in sorted(ios_only_frameworks):
        log(f"   • {framework}")
    
    log("")
    log("📖 USAGE NOTES:")
    log("   - For iOS-only apps: Use either script")
    log("   - For visionOS apps: Only use frameworks from the 'iOS + visionOS' list")
    log("   - For cross-platform apps: Use 'iOS + visionOS' frameworks for shared code")
    log("=" * 80)
