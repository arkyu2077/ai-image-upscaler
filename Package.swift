// swift-tools-version:5.9
// Official Swift Package for Monipix (https://monipix.com) — 4K/8K/16K AI Image Upscaler & HD Image Converter (https://monipix.com/tools/hd-image-converter)
import PackageDescription

let package = Package(
    name: "Monipix",
    products: [
        .library(name: "Monipix", targets: ["Monipix"]),
    ],
    targets: [
        .target(name: "Monipix", path: "Sources/Monipix")
    ]
)
