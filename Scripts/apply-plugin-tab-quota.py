#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}\n--- needle ---\n{old}")
    p.write_text(text.replace(old, new, 1))


# Allow dynamic/user-plugin switcher segments to resolve quota independently of UsageProvider.
path = "Sources/CodexBar/StatusItemController+SwitcherViews.swift"
replace_once(
    path,
    '''    private let showsIcons: Bool
    private let weeklyRemainingProvider: (UsageProvider) -> Double?
    private var buttons: [NSButton] = []
''',
    '''    private let showsIcons: Bool
    private let weeklyRemainingProvider: (UsageProvider) -> Double?
    private let additionalRemainingProvider: (ProviderInstanceID) -> Double?
    private var buttons: [NSButton] = []
''')
replace_once(
    path,
    '''        iconProvider: (UsageProvider) -> NSImage,
        weeklyRemainingProvider: @escaping (UsageProvider) -> Double?,
        onSelect: @escaping (ProviderSwitcherSelection) -> Void)
''',
    '''        iconProvider: (UsageProvider) -> NSImage,
        weeklyRemainingProvider: @escaping (UsageProvider) -> Double?,
        additionalRemainingProvider: @escaping (ProviderInstanceID) -> Double? = { _ in nil },
        onSelect: @escaping (ProviderSwitcherSelection) -> Void)
''')
replace_once(
    path,
    '''        self.showsIcons = showsIcons
        self.weeklyRemainingProvider = weeklyRemainingProvider
        self.stackedIcons = showsIcons && self.segments.count > 3
''',
    '''        self.showsIcons = showsIcons
        self.weeklyRemainingProvider = weeklyRemainingProvider
        self.additionalRemainingProvider = additionalRemainingProvider
        self.stackedIcons = showsIcons && self.segments.count > 3
''')
replace_once(
    path,
    '''    private func remainingPercent(for selection: ProviderSwitcherSelection) -> Double? {
        switch selection {
        case let .provider(instanceID):
            instanceID.firstPartyProvider.flatMap(self.weeklyRemainingProvider)
        case .overview:
            nil
        }
    }
''',
    '''    private func remainingPercent(for selection: ProviderSwitcherSelection) -> Double? {
        switch selection {
        case let .provider(instanceID):
            if let provider = instanceID.firstPartyProvider {
                return self.weeklyRemainingProvider(provider)
            }
            return self.additionalRemainingProvider(instanceID)
        case .overview:
            return nil
        }
    }
''')

# Feed a top-level user plugin's primary usage window into the same switcher indicator path.
path = "Sources/CodexBar/StatusItemController+Menu.swift"
replace_once(
    path,
    '''            weeklyRemainingProvider: { [weak self] provider in
                self?.switcherWeeklyRemaining(for: provider)
            },
            onSelect: { [weak self, weak menu] selection in
''',
    '''            weeklyRemainingProvider: { [weak self] provider in
                self?.switcherWeeklyRemaining(for: provider)
            },
            additionalRemainingProvider: { [weak self] instanceID in
                self?.store.snapshots[instanceID]?.primary?.remainingPercent
            },
            onSelect: { [weak self, weak menu] selection in
''')

# Regression proof: dynamic segments get a live quota ratio while the built-in lane can be absent.
path = "Tests/CodexBarTests/UserPluginTopLevelTests.swift"
replace_once(
    path,
    '''            iconProvider: { _ in NSImage(size: NSSize(width: 16, height: 16)) },
            weeklyRemainingProvider: { _ in nil },
            onSelect: { _ in })
''',
    '''            iconProvider: { _ in NSImage(size: NSSize(width: 16, height: 16)) },
            weeklyRemainingProvider: { _ in nil },
            additionalRemainingProvider: { instanceID in
                instanceID == pluginID ? 62.5 : nil
            },
            onSelect: { _ in })
''')
replace_once(
    path,
    '''        #expect(view._test_segmentSelections() == [
            .provider(UsageProvider.codex.instanceID),
            .provider(pluginID),
        ])
''',
    '''        #expect(view._test_segmentSelections() == [
            .provider(UsageProvider.codex.instanceID),
            .provider(pluginID),
        ])
        let quotaRatios = view._test_quotaIndicatorFillRatios()
        #expect(quotaRatios.count == 1)
        #expect(abs((quotaRatios.first ?? 0) - 0.625) < 0.0001)
''')

print("Applied dynamic user-plugin switcher quota support.")
