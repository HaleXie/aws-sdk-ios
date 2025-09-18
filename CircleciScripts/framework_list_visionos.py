# A list of frameworks/packages for the AWS iOS SDK that are compatible with visionOS.
# This excludes modules that use APIs not available on visionOS platform.
# 
# Excluded from visionOS (verified by build testing):
# - AWSCognitoIdentityProviderASF: Uses UIScreen.mainScreen (unavailable on visionOS) - reverted fix
# - AWSCognitoAuth: Uses Safari Services (SFSafariViewControllerDelegate, SFAuthenticationSession unavailable on visionOS)
# - AWSCognitoIdentityProvider: Depends on AWSCognitoIdentityProviderASF
# - AWSGoogleSignIn: Uses keyWindow API (unavailable on visionOS)
# - AWSMobileClient: Includes AWSCognitoAuth source files (inherits Safari Services issues)
# - AWSUserPoolsSignIn: UIScreen dependency issues
# - AWSAuth: Legacy authentication module that depends on incompatible components
#
# Compatible with visionOS (verified by build testing):
# - AWSLex: AVAudioSession is supported on visionOS
# - AWSFacebookSignIn: Builds successfully for visionOS
# - AWSAppleSignIn: Builds successfully for visionOS  
# - AWSAuthUI: Builds successfully for visionOS

# Note that this list maintains the same dependency order as the original framework_list.py
# Packages toward the bottom depend on packages toward the top.

grouped_frameworks_visionos = [
    # No dependencies
    ["AWSCore"],
    [
        # Depends only on AWSCore - all service APIs should work on visionOS
        # Note: AWSAuthCore scheme may be in AWSAuthSDK project, but core auth functionality should work
        "AWSAPIGateway",
        "AWSAutoScaling", 
        "AWSChimeSDKIdentity",
        "AWSChimeSDKMessaging",
        "AWSCloudWatch",
        "AWSComprehend",
        "AWSConnect",
        "AWSConnectParticipant",
        "AWSDynamoDB",
        "AWSEC2",
        "AWSElasticLoadBalancing",
        "AWSIoT",
        "AWSKMS",
        "AWSKinesis",
        "AWSKinesisVideo",
        "AWSKinesisVideoArchivedMedia",
        "AWSKinesisVideoSignaling",
        "AWSKinesisVideoWebRTCStorage",
        "AWSLambda",
        "AWSLex",  # AVAudioSession is supported on visionOS
        "AWSLocation",  # Keep for now, may work with location services
        "AWSLogs",
        "AWSMachineLearning",
        "AWSPinpoint",
        "AWSPolly",
        "AWSRekognition", 
        "AWSS3",
        "AWSSES",
        "AWSSNS",
        "AWSSQS",
        "AWSSageMakerRuntime",
        "AWSSimpleDB",
        "AWSTextract",
        "AWSTranscribe",
        "AWSTranscribeStreaming",
        "AWSTranslate",
    ],
    [
        # These authentication frameworks are actually visionOS-compatible after testing
        "AWSAuthCore",        # Core authentication without UI dependencies
        "AWSFacebookSignIn",  # Facebook authentication - builds successfully on visionOS
        "AWSAppleSignIn",     # Apple Sign In - builds successfully on visionOS
        "AWSAuthUI",          # Authentication UI - builds successfully on visionOS
    ],
    [
        # Framework structure
        "AWSiOSSDKv2",
    ],
]

# Frameworks excluded from XCFramework generation (same as original plus visionOS-incompatible ones)
excluded_from_xcframeworks_visionos = [
    # Original exclusions
    "AWSiOSSDKv2",  # This isn't a real framework
    "AWSAuth",      # Legacy framework not built or packaged
    "AWSMobileClient",  # Named as AWSMobileClientXCF, but also incompatible with visionOS
    "AWSLocation",  # Named as AWSLocationXCF
    
    # visionOS-specific exclusions (these frameworks won't be built for visionOS at all)
    "AWSCognitoIdentityProviderASF",   # UIScreen API unavailable on visionOS (reverted fix)
    "AWSCognitoAuth",                  # Safari Services incompatibility (SFSafariViewControllerDelegate unavailable)
    "AWSCognitoIdentityProvider",      # Depends on AWSCognitoIdentityProviderASF
    "AWSGoogleSignIn",                # Build failures - keyWindow API incompatibility
    "AWSUserPoolsSignIn",             # UIScreen dependency issues
]

def is_framework_included_visionos(framework):
    return framework not in excluded_from_xcframeworks_visionos

# flatten the grouped frameworks
frameworks_visionos = [framework for group in grouped_frameworks_visionos for framework in group]

# Create the final list of frameworks for visionOS XCFramework generation
xcframeworks_visionos = list(filter(is_framework_included_visionos, frameworks_visionos)) + ["AWSLocationXCF"]
# Note: AWSMobileClientXCF is excluded for visionOS due to authentication dependencies

# List of frameworks that should only be built for iOS (not visionOS)
ios_only_frameworks = [
    "AWSCognitoIdentityProviderASF",   # UIScreen API unavailable on visionOS (reverted fix)
    "AWSCognitoAuth",                  # Safari Services APIs unavailable (SFSafariViewControllerDelegate, SFAuthenticationSession)
    "AWSCognitoIdentityProvider",      # Depends on AWSCognitoIdentityProviderASF
    "AWSGoogleSignIn",                # keyWindow API unavailable on visionOS
    "AWSMobileClient",                # Includes AWSCognitoAuth source files (inherits Safari Services issues)
    "AWSUserPoolsSignIn",             # UIScreen dependency issues
    "AWSAuth",                        # Legacy module with dependencies on incompatible components
]