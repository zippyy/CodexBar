#if canImport(JavaScriptCore)
import AppKit
import Foundation
import Testing
@testable import CodexBar
@testable import CodexBarCore

@Suite(.serialized)
struct UserPluginTopLevelTests {
    @Test
    func `topLevel manifest flag defaults false and accepts booleans`() throws {
        let base: [String: Any] = [
            "id": "top-level-meter",
            "name": "Top Level Meter",
            "endpoints": ["https://example.com"],
            "settings": [],
        ]
        let defaultManifest = try ProviderPluginManifest(
            definition: JSONProviderPluginValue(base),
            allowsDynamicID: true)
        #expect(defaultManifest.topLevel == false)

        var optedIn = base
        optedIn["topLevel"] = true
        let topLevelManifest = try ProviderPluginManifest(
            definition: JSONProviderPluginValue(optedIn),
            allowsDynamicID: true)
        #expect(topLevelManifest.topLevel == true)

        var invalid = base
        invalid["topLevel"] = "true"
        #expect(throws: ProviderPluginError.self) {
            _ = try ProviderPluginManifest(
                definition: JSONProviderPluginValue(invalid),
                allowsDynamicID: true)
        }
    }

    @Test @MainActor
    func `provider switcher accepts a dynamic top level segment`() throws {
        let pluginID = try #require(ProviderInstanceID(rawValue: "nous-portal"))
        let pluginIcon = NSImage(size: NSSize(width: 16, height: 16))
        let view = ProviderSwitcherView(
            providers: [.codex],
            additionalSegments: [
                ProviderSwitcherAdditionalSegment(
                    instanceID: pluginID,
                    image: pluginIcon,
                    title: "Nous Portal"),
            ],
            selected: .provider(pluginID),
            includesOverview: false,
            width: 310,
            showsIcons: true,
            iconProvider: { _ in NSImage(size: NSSize(width: 16, height: 16)) },
            weeklyRemainingProvider: { _ in nil },
            additionalRemainingProvider: { instanceID in
                instanceID == pluginID ? 62.5 : nil
            },
            onSelect: { _ in })

        #expect(view._test_segmentSelections() == [
            .provider(UsageProvider.codex.instanceID),
            .provider(pluginID),
        ])
        let quotaRatios = view._test_quotaIndicatorFillRatios()
        #expect(quotaRatios.count == 1)
        #expect(abs((quotaRatios.first ?? 0) - 0.625) < 0.0001)
    }
}
#endif
