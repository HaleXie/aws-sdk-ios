// swift-tools-version: 6.0
import PackageDescription
import class Foundation.FileManager
import struct Foundation.URL

// Current stable version of the AWS iOS SDK
//
// This value will be updated by the CI/CD pipeline and should not be
// updated manually
let latestVersion = "2.41.0-visionOS"

// Hosting url where the release artifacts are hosted.
let hostingUrl = "https://github.com/HaleXie/aws-sdk-ios-spm/releases/download/2.41.0-visionOS-1/"

enum BuildMode {
    case remote
    case localWithDictionary
    case localWithFilesystem
}

let localPath = "XCF"
let buildMode = BuildMode.remote

// Map between the available frameworks and the checksum
//
// The checksum value will be updated by the CI/CD pipeline and should
// not be updated manually
let frameworksToChecksum = [
    "AWSAPIGateway": "84bf483708694b7c2b44881c65d4ff400c240298db141a749c06974c93b4a26a",
    "AWSAppleSignIn": "db6b03e0811d84c4797eb16d722e09c21f301da44746a670b8cb2a65eaf56770",
    "AWSAuthCore": "ad3e36b2209c5a8a198d5b5288bdde3283e8e7895ab6cdf176c38310824120e4",
    "AWSAuthUI": "73c64172ef113da4b6f1e94f11ccdf2713b2621de4e8d3314c6ea1408fa45725",
    "AWSAutoScaling": "dbc14a8494616ae69a634d2797b46293a51212b249d0bb025e452e0b5748affb",
    "AWSChimeSDKIdentity": "9ce558657340aeb34e5e206aab1b5700a28304733ebc77a828d86cae773f311e",
    "AWSChimeSDKMessaging": "f9dcdcf3e8855fc6fe2ead887cb2a160f567fc3960cbcfee3228bcfac64d5afe",
    "AWSCloudWatch": "aa901bf2e34e15f8e370faf312becb3cce8491a0d5fd3d195f106676a0336b8b",
    "AWSCognitoAuth": "1494c07cda115aa1db2d17b3c63f7837e3d9a64e251cb0c86c4682251afe1417",
    "AWSCognitoIdentityProvider": "74c7a2f03e40e587cbefd5dc26635d450cbb70dc6130cb1561557a8e47bf8a82",
    "AWSCognitoIdentityProviderASF": "e8d0d431d02424baf378f96cd85117fbabb384e3a2fa53a75225e802d03b1edf",
    "AWSComprehend": "d11de3ffdcf7b421bb5d9cf8d35325e50e1dbf4c1548cb29f1684c95ccb501f6",
    "AWSConnect": "c82983da2aa24f5148006dcb182d56707d3dc06f9aec656cb3814fe969d8aacd",
    "AWSConnectParticipant": "d60186ae90ff55880d4a0e549e0623dea9ab90425b8653e9309e0382056ea78d",
    "AWSCore": "4149d7d5c33cfae2ff3df370fd6cf5c862ec8cacc11dc17a9059bc5cfb56473e",
    "AWSDynamoDB": "0d52dd7fcc8bc6787f47fc1cd083f87a07207e9c2e8023ba47b26b16fd55a843",
    "AWSEC2": "f0e9aa4d54a60e111555c65ebd830f070f9dc1db5631b8521356b5ca2c453a59",
    "AWSElasticLoadBalancing": "7490398fd4546d08847515afff92b65821a732f11da653df554dd4aa757a12ad",
    "AWSFacebookSignIn": "fae8dcd9bf85c20a882978b676446b5f5057e25c8c05e9e300706fe02c46aa64",
    "AWSGoogleSignIn": "53c117441ed17d133bbd207082ea561ffcb683e1735a0daa31696fb1ec135d49",
    "AWSIoT": "e8d01c87518379b317faa08388190741fcdf00b6cff17b2f997d26b8c23e7cd5",
    "AWSKMS": "8011ee85faf5450a7cdbb91b4b0d8d73e792c6aa189e84e44bb3b1b5ec766395",
    "AWSKinesis": "add47600914ce0a9a5a5d12be201506e248bd404eb32542f2a372696a142736c",
    "AWSKinesisVideo": "9f993ae1dd90f20148682fb478c68c495db5705536134bb0da4af89de449bd8a",
    "AWSKinesisVideoArchivedMedia": "ae63dec2a2e5ec400c9711cb1f7aa9c1550c5a7dafd56472245167faa4e7aa81",
    "AWSKinesisVideoSignaling": "4c2224c22a9b15346e74de244442ad75b8b3e28ab58b299cedf74afa49e89cda",
    "AWSKinesisVideoWebRTCStorage": "c8aea44c90568a67b5fffe9a5ddc1bddd353c349bdb2618397f4881de004e76f",
    "AWSLambda": "bca353cc7247aa3df57337bc7b74887826dae1fa4be7e78830fb418116e37445",
    "AWSLex": "5893dd2408e923f4e907b32747e038cf5a812bdb75131571595a1b3d90a5e5c5",
    "AWSLocationXCF": "baecee6b4d457d17ebfe2fd7cf63f29e38bc205c4bc15e051b3b13689fe8a44b",
    "AWSLogs": "dbdee024db6a3fa42b3b4742ec715f59e47bd8b50dcc564eede123d8fe9df7e1",
    "AWSMachineLearning": "f2abf416244449eca7aff4badaf389895c0b0be54d77d2d6516827ef734c31b7",
    "AWSMobileClientXCF": "8407c1748dc9ee3600dd7691acc52114540029045506878afe66503acfc6c24a",
    "AWSPinpoint": "d3ce93a952dc8b44fef35e58892326f23e5acd209b3d0e3ff4cf69ddfb52a4f1",
    "AWSPolly": "02ad0e4cfca6530c8368a60a9dfb45ad63499b500009e1c28d8b5ba93a3b5aa1",
    "AWSRekognition": "d3f9fc1165ed0dc84c69dbf4f23c47fc50a901ff4aaa672ee4f9e08d1941f42e",
    "AWSS3": "0aafb9e5f6e92b925a370c34656dfe613e36de9146c0c07281ecb97a9e711c05",
    "AWSSES": "0badc138e3d930ac1aad35724fcb10da505f3866aff7dfd959a74fd848e84374",
    "AWSSNS": "5fcecf4161d7bc762651b5db93c22d6ac78b406ec8166f4ed2a5f087045f669e",
    "AWSSQS": "2f7429a7db5a53860a55f2c2bd4c426764dceb007681e5835bd3c3e96e4dd1d3",
    "AWSSageMakerRuntime": "a4ab069309aed60facb9aff1cdb08a427faf6a0a89857fd2eea74ac6ff6dfce9",
    "AWSSimpleDB": "714f8048c42b8977d47a951160939db91ad473a7c8c84a6f91209bc62a03ea9d",
    "AWSTextract": "69fdd87ae9a738e75f77dcf392d8824d2f21089331482376fe390c0c1327f663",
    "AWSTranscribe": "e27d0d99de531b059308109647cd35b4b23b2b926eefb3773aea5f0e17fac7ee",
    "AWSTranscribeStreaming": "4c50d06b14a450caf81267030999c180fbd960a7e5a3203fe1bc30c558e1badd",
    "AWSTranslate": "3eb19bea8b07c7ac111a1888db2e9f702150f211c57577462b8e4e1953e5d7fe",
    "AWSUserPoolsSignIn": "15cb977a9e5b1f2f58a0e0f56a313c8c7cb54f439959843f531719aae0d36041",
]


extension Target.Dependency {
    // Framework dependencies present in the SDK
    static let awsCore: Self = .target(name: "AWSCore")
    static let awsAuthCore: Self = .target(name: "AWSAuthCore")
    static let awsCognitoIdentityProviderASF: Self = .target(name: "AWSCognitoIdentityProviderASF")
    static let awsCognitoIdentityProvider: Self = .target(name: "AWSCognitoIdentityProvider")
}

let depdenencyMap: [String: [Target.Dependency]] = [
    "AWSAPIGateway": [.awsCore],
    "AWSAppleSignIn": [.awsCore, .awsAuthCore],
    "AWSAuthCore": [.awsCore],
    "AWSAuthUI": [.awsCore, .awsAuthCore],
    "AWSAutoScaling": [.awsCore],
    "AWSChimeSDKIdentity": [.awsCore],
    "AWSChimeSDKMessaging": [.awsCore],
    "AWSCloudWatch": [.awsCore],
    "AWSCognitoAuth": [.awsCore, .awsCognitoIdentityProviderASF],
    "AWSCognitoIdentityProvider": [.awsCore, .awsCognitoIdentityProviderASF],
    "AWSCognitoIdentityProviderASF": [.awsCore],
    "AWSComprehend": [.awsCore],
    "AWSConnect": [.awsCore],
    "AWSConnectParticipant": [.awsCore],
    "AWSCore": [],
    "AWSDynamoDB": [.awsCore],
    "AWSEC2": [.awsCore],
    "AWSElasticLoadBalancing": [.awsCore],
    "AWSFacebookSignIn": [.awsCore, .awsAuthCore],
    "AWSGoogleSignIn": [.awsCore, .awsAuthCore],
    "AWSIoT": [.awsCore],
    "AWSKMS": [.awsCore],
    "AWSKinesis": [.awsCore],
    "AWSKinesisVideo": [.awsCore],
    "AWSKinesisVideoArchivedMedia": [.awsCore],
    "AWSKinesisVideoSignaling": [.awsCore],
    "AWSKinesisVideoWebRTCStorage": [.awsCore],
    "AWSLambda": [.awsCore],
    "AWSLex": [.awsCore],
    "AWSLocationXCF": [.awsCore],
    "AWSLogs": [.awsCore],
    "AWSMachineLearning": [.awsCore],
    "AWSMobileClientXCF": [.awsAuthCore, .awsCognitoIdentityProvider],
    "AWSPinpoint": [.awsCore],
    "AWSPolly": [.awsCore],
    "AWSRekognition": [.awsCore],
    "AWSS3": [.awsCore],
    "AWSSES": [.awsCore],
    "AWSSNS": [.awsCore],
    "AWSSQS": [.awsCore],
    "AWSSageMakerRuntime": [.awsCore],
    "AWSSimpleDB": [.awsCore],
    "AWSTextract": [.awsCore],
    "AWSTranscribe": [.awsCore],
    "AWSTranscribeStreaming": [.awsCore],
    "AWSTranslate": [.awsCore],
    "AWSUserPoolsSignIn": [.awsCognitoIdentityProvider, .awsAuthCore, .awsCore]
]


var frameworksOnFilesystem: [String] {
    let fileManager = FileManager.default
    let rootURL = URL(fileURLWithPath: #file).deletingLastPathComponent()
    let xcfURL = rootURL.appendingPathComponent(localPath)
    let paths = (try? fileManager.contentsOfDirectory(atPath: xcfURL.path)) ?? []
    let frameworks = paths
        .filter { $0.hasSuffix(".xcframework") }
        .map { xcfURL.appendingPathComponent($0) }
        .map { $0.deletingPathExtension().lastPathComponent }
        .sorted()
    return frameworks
}

var frameworksFromDictionary: [String] {
    frameworksToChecksum.map { $0.key }.sorted()
}

let frameworks = buildMode == .localWithFilesystem ? frameworksOnFilesystem : frameworksFromDictionary

func createProducts() -> [Product] {
    let products: [Product]
    if buildMode != .remote {
        products = frameworks.map { Product.library(name: $0, targets: [$0]) }
    } else {
        products = frameworks.map { framework -> Product in
            if depdenencyMap[framework]!.isEmpty {
                return Product.library(name: framework, targets: [framework])
            }
            // If framework has dependencies, create a `<framework>-Target`
            // library that is used to link framework target with its dependencies
            return Product.library(name: framework, targets: ["\(framework)-Target"])
        }
    }
    return products
}

func createTarget(framework: String, checksum: String = "") -> Target {
    buildMode != .remote ?
        Target.binaryTarget(name: framework,
                            path: "\(localPath)/\(framework).xcframework") :
        Target.binaryTarget(name: framework,
                            url: "\(hostingUrl)\(framework)-\(latestVersion).zip",
                            checksum: checksum)
}

func createTargets() -> [Target] {
    let targets: [Target]
    if buildMode != .remote {
        targets = frameworks.map {
            createTarget(framework: $0)
        }
    } else {
        targets = frameworksToChecksum.flatMap { framework, checksum -> [Target] in
            var targets = [createTarget(framework: framework, checksum: checksum)]

            // If the framework has dependencies, create an additional target that links the
            // framework and its depedencies using the previously created product.
            if var dependencies = depdenencyMap[framework], !dependencies.isEmpty {
                dependencies.append(.target(name: framework))
                targets.append(
                    .target(
                        name: "\(framework)-Target",
                        dependencies: dependencies,
                        path: "DependantTargets/\(framework)-Target",
                        sources: ["empty.m"],
                        publicHeadersPath: "."
                    )
                )
            }
            return targets
        }
    }
    return targets
}

let products = createProducts()
let targets = createTargets()

let package = Package(
    name: "AWSiOSSDKV2",
    platforms: [
        .iOS(.v12),
        .visionOS(.v2)
    ],
    products: products,
    targets: targets
)
