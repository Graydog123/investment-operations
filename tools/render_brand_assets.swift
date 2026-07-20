#!/usr/bin/env swift
// SPDX-License-Identifier: MIT

import AppKit
import Foundation

guard CommandLine.arguments.count == 4 else {
    fputs("Usage: render_brand_assets.swift <art.png> <hero.png> <social.jpg>\n", stderr)
    exit(2)
}

let artURL = URL(fileURLWithPath: CommandLine.arguments[1])
let heroURL = URL(fileURLWithPath: CommandLine.arguments[2])
let socialURL = URL(fileURLWithPath: CommandLine.arguments[3])

guard let art = NSImage(contentsOf: artURL) else {
    fputs("Cannot read source artwork.\n", stderr)
    exit(1)
}

let canvasSize = NSSize(width: 1600, height: 800)
let canvas = NSImage(size: canvasSize)

func color(_ hex: UInt32, alpha: CGFloat = 1) -> NSColor {
    NSColor(
        red: CGFloat((hex >> 16) & 0xff) / 255,
        green: CGFloat((hex >> 8) & 0xff) / 255,
        blue: CGFloat(hex & 0xff) / 255,
        alpha: alpha
    )
}

func drawText(
    _ text: String,
    x: CGFloat,
    top: CGFloat,
    font: NSFont,
    textColor: NSColor,
    kern: CGFloat = 0
) {
    let attributes: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: textColor,
        .kern: kern,
    ]
    let size = (text as NSString).size(withAttributes: attributes)
    let point = NSPoint(x: x, y: canvasSize.height - top - size.height)
    (text as NSString).draw(at: point, withAttributes: attributes)
}

canvas.lockFocus()
color(0xF2E3C5).setFill()
NSRect(origin: .zero, size: canvasSize).fill()

let artHeight = CGFloat(758)
let artRect = NSRect(x: 0, y: (canvasSize.height - artHeight) / 2, width: 1600, height: artHeight)
art.draw(in: artRect, from: NSRect(origin: .zero, size: art.size), operation: .sourceOver, fraction: 1)

color(0xC96A32).setFill()
NSRect(x: 100, y: canvasSize.height - 180, width: 96, height: 6).fill()

drawText(
    "INVESTMENT OPERATIONS",
    x: 100,
    top: 118,
    font: NSFont.systemFont(ofSize: 24, weight: .medium),
    textColor: color(0x7B6049),
    kern: 3.2
)
drawText(
    "投资经营学",
    x: 94,
    top: 205,
    font: NSFont.systemFont(ofSize: 104, weight: .bold),
    textColor: color(0x102B3A)
)
drawText(
    "像经营一家餐馆一样思考股票",
    x: 100,
    top: 354,
    font: NSFont.systemFont(ofSize: 41, weight: .medium),
    textColor: color(0x314754)
)
drawText(
    "生活  →  经营  →  金融  →  投资",
    x: 100,
    top: 442,
    font: NSFont.systemFont(ofSize: 27, weight: .regular),
    textColor: color(0x7B6049)
)
drawText(
    "开放思想体系 · 鬼谷子",
    x: 100,
    top: 654,
    font: NSFont.systemFont(ofSize: 25, weight: .regular),
    textColor: color(0x314754)
)
canvas.unlockFocus()

guard
    let heroTIFF = canvas.tiffRepresentation,
    let heroBitmap = NSBitmapImageRep(data: heroTIFF),
    let heroPNG = heroBitmap.representation(using: .png, properties: [:])
else {
    fputs("Cannot encode hero PNG.\n", stderr)
    exit(1)
}
try heroPNG.write(to: heroURL)

let social = NSImage(size: NSSize(width: 1280, height: 640))
social.lockFocus()
canvas.draw(
    in: NSRect(x: 0, y: 0, width: 1280, height: 640),
    from: NSRect(origin: .zero, size: canvasSize),
    operation: .copy,
    fraction: 1
)
social.unlockFocus()

guard
    let socialTIFF = social.tiffRepresentation,
    let socialBitmap = NSBitmapImageRep(data: socialTIFF),
    let socialJPEG = socialBitmap.representation(using: .jpeg, properties: [.compressionFactor: 0.9])
else {
    fputs("Cannot encode social preview JPEG.\n", stderr)
    exit(1)
}
try socialJPEG.write(to: socialURL)

print("Rendered \(heroURL.path) and \(socialURL.path)")
