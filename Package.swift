// swift-tools-version: 6.2
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "Kliply",
    platforms: [.macOS(.v14)],
    products: [
        .executable(name: "Kliply", targets: ["Kliply"])
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "Kliply",
            dependencies: [],
            resources: [
                .process("Resources"),
                .process("PrivacyInfo.xcprivacy")
            ]
        ),
        .testTarget(
            name: "KliplyTests",
            dependencies: ["Kliply"]
        )
    ]
)
