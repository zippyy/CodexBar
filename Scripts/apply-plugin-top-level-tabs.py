#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}: {old[:80]!r}")
    p.write_text(text.replace(old, new, 1))


def replace_all(path: str, old: str, new: str, expected: int) -> None:
    p = ROOT / path
    text = p.read_text()
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{path}: expected {expected} matches, found {count}: {old[:80]!r}")
    p.write_text(text.replace(old, new))


# ProviderPluginValue: expose booleans to manifest parsing on every engine.
path = "Sources/CodexBarCore/Plugins/ProviderPluginEngine.swift"
replace_once(path,
'''    var isUndefined: Bool { get }\n    var isString: Bool { get }\n''',
'''    var isUndefined: Bool { get }\n    var isBoolean: Bool { get }\n    var isString: Bool { get }\n''')
replace_once(path,
'''    func stringValue() -> String\n    func int32Value() -> Int32\n''',
'''    func stringValue() -> String\n    func boolValue() -> Bool\n    func int32Value() -> Int32\n''')
replace_once(path,
'''    var isUndefined: Bool {\n        false\n    }\n\n    var isString: Bool {\n''',
'''    var isUndefined: Bool {\n        false\n    }\n\n    var isBoolean: Bool {\n        guard let number = self.value as? NSNumber else { return false }\n        return CFGetTypeID(number) == CFBooleanGetTypeID()\n    }\n\n    var isString: Bool {\n''')
replace_once(path,
'''    func stringValue() -> String {\n        self.value as? String ?? String(describing: self.value)\n    }\n\n    func int32Value() -> Int32 {\n''',
'''    func stringValue() -> String {\n        self.value as? String ?? String(describing: self.value)\n    }\n\n    func boolValue() -> Bool {\n        (self.value as? NSNumber)?.boolValue ?? false\n    }\n\n    func int32Value() -> Int32 {\n''')
replace_once(path,
'''    var isUndefined: Bool {\n        self.value.isUndefined\n    }\n\n    var isString: Bool {\n''',
'''    var isUndefined: Bool {\n        self.value.isUndefined\n    }\n\n    var isBoolean: Bool {\n        self.value.isBoolean\n    }\n\n    var isString: Bool {\n''')
replace_once(path,
'''    func stringValue() -> String {\n        self.value.toString()\n    }\n\n    func int32Value() -> Int32 {\n''',
'''    func stringValue() -> String {\n        self.value.toString()\n    }\n\n    func boolValue() -> Bool {\n        self.value.toBool()\n    }\n\n    func int32Value() -> Int32 {\n''')

path = "Sources/CodexBarCore/Plugins/QuickJSProviderPluginEngine.swift"
replace_once(path,
'''    var isUndefined: Bool {\n        cqjs_is_undefined(self.value)\n    }\n\n    var isString: Bool {\n''',
'''    var isUndefined: Bool {\n        cqjs_is_undefined(self.value)\n    }\n\n    var isBoolean: Bool {\n        JS_IsBool(self.value)\n    }\n\n    var isString: Bool {\n''')
replace_once(path,
'''    func stringValue() -> String {\n        (try? self.engine.string(from: self.value)) ?? ""\n    }\n\n    func int32Value() -> Int32 {\n''',
'''    func stringValue() -> String {\n        (try? self.engine.string(from: self.value)) ?? ""\n    }\n\n    func boolValue() -> Bool {\n        JS_ToBool(self.engine.context, self.value) != 0\n    }\n\n    func int32Value() -> Int32 {\n''')

# Manifest: topLevel is presentation-only and defaults off.
path = "Sources/CodexBarCore/Plugins/ProviderPluginManifest.swift"
replace_once(path,
'''    public let id: ProviderInstanceID\n    public let name: String\n    public let icon: ProviderPluginIcon\n''',
'''    public let id: ProviderInstanceID\n    public let name: String\n    public let topLevel: Bool\n    public let icon: ProviderPluginIcon\n''')
replace_once(path,
'''        self.id = id\n        self.name = try Self.boundedString(definition, property: "name", maximumLength: 80)\n        self.icon = try Self.parseIcon(definition.property("icon"), fallbackName: self.name)\n''',
'''        self.id = id\n        self.name = try Self.boundedString(definition, property: "name", maximumLength: 80)\n        self.topLevel = try Self.optionalBool(definition, property: "topLevel") ?? false\n        self.icon = try Self.parseIcon(definition.property("icon"), fallbackName: self.name)\n''')
replace_once(path,
'''    private static func requiredString(_ object: any ProviderPluginValue, property: String) throws -> String {\n''',
'''    private static func optionalBool(_ object: any ProviderPluginValue, property: String) throws -> Bool? {\n        guard let value = object.property(property), !value.isUndefined, !value.isNull else { return nil }\n        guard value.isBoolean else {\n            throw ProviderPluginError.invalidManifest("'\\(property)' must be a boolean when present")\n        }\n        return value.boolValue()\n    }\n\n    private static func requiredString(_ object: any ProviderPluginValue, property: String) throws -> String {\n''')

# TypeScript contract.
path = "Sources/CodexBarCore/Resources/Plugins/codexbar-plugin.d.ts"
replace_once(path,
'''  id: string;\n  name: string;\n  icon?: { monogram?: string; tint?: string };\n''',
'''  id: string;\n  name: string;\n  /** Show this user plugin as a first-class provider tab in the merged provider switcher. */\n  topLevel?: boolean;\n  icon?: { monogram?: string; tint?: string };\n''')

# Switcher: preserve the existing built-in initializer contract while allowing dynamic segments.
path = "Sources/CodexBar/StatusItemController+SwitcherViews.swift"
replace_once(path,
'''enum ProviderSwitcherSelection: Hashable {\n    case overview\n    case provider(ProviderInstanceID)\n}\n\nfinal class ProviderSwitcherView: NSView {\n''',
'''enum ProviderSwitcherSelection: Hashable {\n    case overview\n    case provider(ProviderInstanceID)\n}\n\nstruct ProviderSwitcherAdditionalSegment {\n    let instanceID: ProviderInstanceID\n    let image: NSImage\n    let title: String\n}\n\nfinal class ProviderSwitcherView: NSView {\n''')
replace_once(path,
'''    init(\n        providers: [UsageProvider],\n        selected: ProviderSwitcherSelection?,\n''',
'''    init(\n        providers: [UsageProvider],\n        additionalSegments: [ProviderSwitcherAdditionalSegment] = [],\n        selected: ProviderSwitcherSelection?,\n''')
replace_once(path,
'''        var segments = providers.map { provider in\n            let fullTitle = Self.switcherTitle(for: provider)\n            let icon = iconProvider(provider)\n            icon.isTemplate = true\n            // Avoid any resampling: we ship exact 16pt/32px assets for crisp rendering.\n            icon.size = NSSize(width: 16, height: 16)\n            return Segment(\n                selection: .provider(provider.instanceID),\n                image: icon,\n                title: fullTitle)\n        }\n        if includesOverview {\n''',
'''        var segments = providers.map { provider in\n            let fullTitle = Self.switcherTitle(for: provider)\n            let icon = iconProvider(provider)\n            icon.isTemplate = true\n            // Avoid any resampling: we ship exact 16pt/32px assets for crisp rendering.\n            icon.size = NSSize(width: 16, height: 16)\n            return Segment(\n                selection: .provider(provider.instanceID),\n                image: icon,\n                title: fullTitle)\n        }\n        segments.append(contentsOf: additionalSegments.map { segment in\n            segment.image.isTemplate = true\n            segment.image.size = NSSize(width: 16, height: 16)\n            return Segment(\n                selection: .provider(segment.instanceID),\n                image: segment.image,\n                title: segment.title)\n        })\n        if includesOverview {\n''')
replace_once(path,
'''    func _test_buttonFrames() -> [NSRect] {\n''',
'''    func _test_segmentSelections() -> [ProviderSwitcherSelection] {\n        self.segments.map(\\.selection)\n    }\n\n    func _test_buttonFrames() -> [NSRect] {\n''')

# User plugin presentation helpers and filtering.
path = "Sources/CodexBar/StatusItemController+UserPlugins.swift"
replace_once(path,
'''extension StatusItemController {\n    func addUserPluginMenuCards(to menu: NSMenu, width: CGFloat) {\n        let plugins = UserProviderPluginRegistry.all.filter { self.settings.isPluginEnabled($0.manifest.id) }\n        guard !plugins.isEmpty else { return }\n''',
'''extension StatusItemController {\n    func enabledTopLevelUserPlugins() -> [UserProviderPlugin] {\n        UserProviderPluginRegistry.all.filter { plugin in\n            plugin.manifest.topLevel && self.settings.isPluginEnabled(plugin.manifest.id)\n        }\n    }\n\n    func isEnabledTopLevelUserPlugin(_ instanceID: ProviderInstanceID) -> Bool {\n        self.enabledTopLevelUserPlugins().contains { $0.manifest.id == instanceID }\n    }\n\n    func mergedSwitcherProviderIDs(firstPartyProviders: [UsageProvider]) -> [ProviderInstanceID] {\n        firstPartyProviders.map(\\.instanceID) + self.enabledTopLevelUserPlugins().map { $0.manifest.id }\n    }\n\n    func hasMergedProviderSwitcher(firstPartyProviders: [UsageProvider]) -> Bool {\n        self.shouldMergeIcons && self.mergedSwitcherProviderIDs(firstPartyProviders: firstPartyProviders).count > 1\n    }\n\n    func userPluginSwitcherSegments() -> [ProviderSwitcherAdditionalSegment] {\n        self.enabledTopLevelUserPlugins().map { plugin in\n            ProviderSwitcherAdditionalSegment(\n                instanceID: plugin.manifest.id,\n                image: self.userPluginSwitcherIcon(monogram: plugin.manifest.icon.monogram),\n                title: plugin.manifest.name)\n        }\n    }\n\n    private func userPluginSwitcherIcon(monogram: String) -> NSImage {\n        let size = NSSize(width: 16, height: 16)\n        let image = NSImage(size: size)\n        image.lockFocus()\n        let text = String(monogram.prefix(2)) as NSString\n        let font = NSFont.systemFont(ofSize: text.length > 1 ? 7.5 : 10, weight: .bold)\n        let attributes: [NSAttributedString.Key: Any] = [\n            .font: font,\n            .foregroundColor: NSColor.labelColor,\n        ]\n        let textSize = text.size(withAttributes: attributes)\n        text.draw(\n            at: NSPoint(x: (size.width - textSize.width) / 2, y: (size.height - textSize.height) / 2),\n            withAttributes: attributes)\n        image.unlockFocus()\n        image.isTemplate = true\n        return image\n    }\n\n    func addUserPluginMenuCards(\n        to menu: NSMenu,\n        width: CGFloat,\n        selectedTopLevelPluginID: ProviderInstanceID? = nil)\n    {\n        let enabledPlugins = UserProviderPluginRegistry.all.filter { self.settings.isPluginEnabled($0.manifest.id) }\n        let plugins: [UserProviderPlugin]\n        if let selectedTopLevelPluginID {\n            plugins = enabledPlugins.filter {\n                $0.manifest.topLevel && $0.manifest.id == selectedTopLevelPluginID\n            }\n        } else if self.shouldMergeIcons {\n            // A top-level plugin owns its switcher tab; do not duplicate it under every built-in tab.\n            plugins = enabledPlugins.filter { !$0.manifest.topLevel }\n        } else {\n            // Split-icon mode has no dynamic provider switcher yet, so preserve the legacy global-card behavior.\n            plugins = enabledPlugins\n        }\n        guard !plugins.isEmpty else { return }\n''')

# Menu: combine built-ins and opted-in plugins in the switcher and render selected plugin alone.
path = "Sources/CodexBar/StatusItemController+Menu.swift"
replace_once(path,
'''        let enabledProviders = self.store.enabledFirstPartyProvidersForDisplay()\n        let includesOverview = self.includesOverviewTab(enabledProviders: enabledProviders)\n        let switcherSelection = self.shouldMergeIcons && enabledProviders.count > 1\n            ? self.resolvedSwitcherSelection(\n                enabledProviders: enabledProviders,\n                includesOverview: includesOverview)\n            : nil\n        let isOverviewSelected = switcherSelection == .overview\n        let selectedProvider = if isOverviewSelected {\n            self.resolvedMenuProvider(enabledProviders: enabledProviders)\n        } else {\n            switcherSelection?.provider ?? provider\n        }\n        // Provider-specific by design: Codex remains the empty merged-menu selection fallback.\n        let currentProvider = selectedProvider ?? enabledProviders.first ?? .codex\n        let rawCodexAccountDisplay = isOverviewSelected ? nil : self.codexAccountMenuDisplay(for: currentProvider)\n        let codexAccountDisplay = isOverviewSelected\n            ? nil\n            : self.stableCodexAccountMenuDisplay(\n                rawCodexAccountDisplay,\n                menu: menu,\n                provider: currentProvider)\n        let tokenAccountDisplay = isOverviewSelected ? nil : self.tokenAccountMenuDisplay(for: currentProvider)\n''',
'''        let enabledProviders = self.store.enabledFirstPartyProvidersForDisplay()\n        let switcherProviderIDs = self.mergedSwitcherProviderIDs(firstPartyProviders: enabledProviders)\n        let hasMergedSwitcher = self.shouldMergeIcons && switcherProviderIDs.count > 1\n        let includesOverview = self.includesOverviewTab(enabledProviders: enabledProviders)\n        let switcherSelection = hasMergedSwitcher\n            ? self.resolvedSwitcherSelection(\n                enabledProviders: enabledProviders,\n                includesOverview: includesOverview)\n            : nil\n        let isOverviewSelected = switcherSelection == .overview\n        let selectedTopLevelPluginID = switcherSelection?.instanceID.flatMap { instanceID in\n            self.isEnabledTopLevelUserPlugin(instanceID) ? instanceID : nil\n        }\n        let isTopLevelPluginSelected = selectedTopLevelPluginID != nil\n        let selectedProvider = if isOverviewSelected {\n            self.resolvedMenuProvider(enabledProviders: enabledProviders)\n        } else if isTopLevelPluginSelected {\n            nil\n        } else {\n            switcherSelection?.provider ?? provider\n        }\n        // Provider-specific by design: Codex remains the empty merged-menu selection fallback.\n        let currentProvider = selectedProvider ?? enabledProviders.first ?? .codex\n        let suppressProviderSpecificChrome = isOverviewSelected || isTopLevelPluginSelected\n        let rawCodexAccountDisplay = suppressProviderSpecificChrome\n            ? nil\n            : self.codexAccountMenuDisplay(for: currentProvider)\n        let codexAccountDisplay = suppressProviderSpecificChrome\n            ? nil\n            : self.stableCodexAccountMenuDisplay(\n                rawCodexAccountDisplay,\n                menu: menu,\n                provider: currentProvider)\n        let tokenAccountDisplay = suppressProviderSpecificChrome\n            ? nil\n            : self.tokenAccountMenuDisplay(for: currentProvider)\n''')
replace_once(path,
'''        let descriptor = self.makeMenuDescriptor(\n            provider: selectedProvider,\n            includeContextualActions: !isOverviewSelected)\n''',
'''        let descriptor = self.makeMenuDescriptor(\n            provider: selectedProvider,\n            includeContextualActions: !suppressProviderSpecificChrome)\n''')
replace_once(path,
'''        let switcherProvidersMatch = enabledProviders.map(\\.instanceID) == self.lastSwitcherProviders\n''',
'''        let switcherProvidersMatch = switcherProviderIDs == self.lastSwitcherProviders\n''')
replace_all(path,
'''        let canSmartUpdate = self.shouldMergeIcons &&\n            enabledProviders.count > 1 &&\n''',
'''        let canSmartUpdate = hasMergedSwitcher &&\n''', 1)
replace_all(path,
'''        let canPreserveProviderSwitcher = self.shouldMergeIcons &&\n            enabledProviders.count > 1 &&\n''',
'''        let canPreserveProviderSwitcher = hasMergedSwitcher &&\n''', 1)
replace_all(path,
'''            if self.shouldMergeIcons, context.enabledProviders.count > 1 {\n''',
'''            if self.hasMergedProviderSwitcher(firstPartyProviders: context.enabledProviders) {\n''', 1)
replace_all(path,
'''            if self.shouldMergeIcons,\n               context.enabledProviders.count > 1,\n''',
'''            if self.hasMergedProviderSwitcher(firstPartyProviders: context.enabledProviders),\n''', 1)
replace_once(path,
'''        guard self.shouldMergeIcons, enabledProviders.count > 1 else { return }\n        let switcherItem = self.makeProviderSwitcherItem(\n''',
'''        guard self.hasMergedProviderSwitcher(firstPartyProviders: enabledProviders) else { return }\n        let switcherItem = self.makeProviderSwitcherItem(\n''')
replace_once(path,
'''        let view = ProviderSwitcherView(\n            providers: providers,\n            selected: selected,\n''',
'''        let view = ProviderSwitcherView(\n            providers: providers,\n            additionalSegments: self.userPluginSwitcherSegments(),\n            selected: selected,\n''')
replace_once(path,
'''    {\n        if switcherSelection == .overview {\n''',
'''    {\n        if let instanceID = switcherSelection.instanceID,\n           instanceID.firstPartyProvider == nil,\n           self.isEnabledTopLevelUserPlugin(instanceID)\n        {\n            self.addUserPluginMenuCards(\n                to: menu,\n                width: context.menuWidth,\n                selectedTopLevelPluginID: instanceID)\n            return\n        }\n\n        if switcherSelection == .overview {\n''')
replace_once(path,
'''        if includesOverview, self.settings.mergedMenuLastSelectedWasOverview {\n            return .overview\n        }\n        return .provider((self.resolvedMenuProvider(enabledProviders: enabledProviders) ?? .codex).instanceID)\n''',
'''        if includesOverview, self.settings.mergedMenuLastSelectedWasOverview {\n            return .overview\n        }\n        if let selectedMenuProvider = self.selectedMenuProvider,\n           self.isEnabledTopLevelUserPlugin(selectedMenuProvider)\n        {\n            return .provider(selectedMenuProvider)\n        }\n        return .provider((self.resolvedMenuProvider(enabledProviders: enabledProviders) ?? .codex).instanceID)\n''')

# Remember the dynamic switcher membership as part of smart-update compatibility.
path = "Sources/CodexBar/StatusItemController+MenuLocalization.swift"
replace_once(path,
'''        self.lastSwitcherProviders = providers.map(\\.instanceID)\n''',
'''        self.lastSwitcherProviders = self.mergedSwitcherProviderIDs(firstPartyProviders: providers)\n''')

# Keyboard navigation includes top-level plugin tabs.
path = "Sources/CodexBar/StatusItemController+ProviderNavigation.swift"
old = '''    func navigateProviderSwitcher(\n        _ direction: StatusItemMenuProviderNavigationDirection,\n        menu: NSMenu? = nil)\n    {\n        guard self.shouldMergeIcons else { return }\n        let enabledProviders = self.store.enabledFirstPartyProvidersForDisplay()\n        guard enabledProviders.count > 1 else { return }\n\n        let includesOverview = !self.settings.resolvedMergedOverviewProviders(\n            activeProviders: enabledProviders,\n            maxVisibleProviders: SettingsStore.mergedOverviewProviderLimit).isEmpty\n        var selections = enabledProviders.map { ProviderSwitcherSelection.provider($0.instanceID) }\n        if includesOverview {\n            selections.insert(.overview, at: 0)\n        }\n\n        let current: ProviderSwitcherSelection = if includesOverview,\n                                                    self.settings.mergedMenuLastSelectedWasOverview\n        {\n            .overview\n        } else {\n            .provider((self.navigationResolvedProvider(enabledProviders: enabledProviders) ?? .codex).instanceID)\n        }\n        guard let currentIndex = selections.firstIndex(of: current) else { return }\n\n        let delta = direction == .next ? 1 : -1\n        let nextIndex = (currentIndex + delta + selections.count) % selections.count\n        let selection = selections[nextIndex]\n        let menuProvider: UsageProvider = switch selection {\n        case .overview:\n            self.navigationResolvedProvider(enabledProviders: enabledProviders) ?? .codex\n        case let .provider(instanceID):\n            instanceID.firstPartyProvider ?? .codex\n        }\n        self.preservingMergedSwitcherContentCachesDuringInvalidation {\n            switch selection {\n            case .overview:\n                self.settings.mergedMenuLastSelectedWasOverview = true\n                self.lastMenuProvider =\n                    (self.navigationResolvedProvider(enabledProviders: enabledProviders) ?? .codex).instanceID\n            case let .provider(provider):\n                self.settings.mergedMenuLastSelectedWasOverview = false\n                self.selectedMenuProvider = provider\n                self.lastMenuProvider = provider\n            }\n            self.lastMergedSwitcherSelection = selection\n            self.refreshProviderSelectionDependentUI(deferRendering: true)\n        }\n        let trackedMenu = menu ?? self.providerSwitcherShortcutMenuID.flatMap { self.openMenus[$0] }\n        if let trackedMenu {\n            self.requestProviderSwitcherMenuRebuild(\n                trackedMenu,\n                provider: menuProvider)\n        }\n    }\n'''
new = '''    func navigateProviderSwitcher(\n        _ direction: StatusItemMenuProviderNavigationDirection,\n        menu: NSMenu? = nil)\n    {\n        guard self.shouldMergeIcons else { return }\n        let enabledProviders = self.store.enabledFirstPartyProvidersForDisplay()\n        let topLevelPluginIDs = self.enabledTopLevelUserPlugins().map { $0.manifest.id }\n        guard enabledProviders.count + topLevelPluginIDs.count > 1 else { return }\n\n        let includesOverview = !self.settings.resolvedMergedOverviewProviders(\n            activeProviders: enabledProviders,\n            maxVisibleProviders: SettingsStore.mergedOverviewProviderLimit).isEmpty\n        var selections = enabledProviders.map { ProviderSwitcherSelection.provider($0.instanceID) }\n        selections.append(contentsOf: topLevelPluginIDs.map(ProviderSwitcherSelection.provider))\n        if includesOverview {\n            selections.insert(.overview, at: 0)\n        }\n\n        let current = self.resolvedSwitcherSelection(\n            enabledProviders: enabledProviders,\n            includesOverview: includesOverview)\n        guard let currentIndex = selections.firstIndex(of: current) else { return }\n\n        let delta = direction == .next ? 1 : -1\n        let nextIndex = (currentIndex + delta + selections.count) % selections.count\n        let selection = selections[nextIndex]\n        let menuProvider: UsageProvider? = switch selection {\n        case .overview:\n            self.navigationResolvedProvider(enabledProviders: enabledProviders) ?? .codex\n        case let .provider(instanceID):\n            instanceID.firstPartyProvider\n        }\n        self.preservingMergedSwitcherContentCachesDuringInvalidation {\n            switch selection {\n            case .overview:\n                self.settings.mergedMenuLastSelectedWasOverview = true\n                self.lastMenuProvider =\n                    (self.navigationResolvedProvider(enabledProviders: enabledProviders) ?? .codex).instanceID\n            case let .provider(provider):\n                self.settings.mergedMenuLastSelectedWasOverview = false\n                self.selectedMenuProvider = provider\n                self.lastMenuProvider = provider\n            }\n            self.lastMergedSwitcherSelection = selection\n            self.refreshProviderSelectionDependentUI(deferRendering: true)\n        }\n        let trackedMenu = menu ?? self.providerSwitcherShortcutMenuID.flatMap { self.openMenus[$0] }\n        if let trackedMenu {\n            self.requestProviderSwitcherMenuRebuild(\n                trackedMenu,\n                provider: menuProvider)\n        }\n    }\n'''
replace_once(path, old, new)

# Warm sibling caches for plugin tabs too, avoiding first-party account chrome on plugin content.
path = "Sources/CodexBar/StatusItemController+MenuSwitcherWarmup.swift"
replace_once(path,
'''        let enabledProviders = self.store.enabledFirstPartyProvidersForDisplay()\n        guard enabledProviders.count > 1 else { return }\n''',
'''        let enabledProviders = self.store.enabledFirstPartyProvidersForDisplay()\n        let topLevelPluginIDs = self.enabledTopLevelUserPlugins().map { $0.manifest.id }\n        guard enabledProviders.count + topLevelPluginIDs.count > 1 else { return }\n''')
replace_once(path,
'''        var selections: [ProviderSwitcherSelection] = enabledProviders.map { .provider($0.instanceID) }\n        if includesOverview {\n''',
'''        var selections: [ProviderSwitcherSelection] = enabledProviders.map { .provider($0.instanceID) }\n        selections.append(contentsOf: topLevelPluginIDs.map(ProviderSwitcherSelection.provider))\n        if includesOverview {\n''')
replace_once(path,
'''        let isOverviewSelected = selection == .overview\n        let selectedProvider = isOverviewSelected\n            ? self.resolvedMenuProvider(enabledProviders: enabledProviders)\n            : selection.provider\n        let currentProvider = selectedProvider ?? enabledProviders.first ?? .codex\n        let codexAccountDisplay = isOverviewSelected ? nil : self.codexAccountMenuDisplay(for: currentProvider)\n        let tokenAccountDisplay = isOverviewSelected ? nil : self.tokenAccountMenuDisplay(for: currentProvider)\n''',
'''        let isOverviewSelected = selection == .overview\n        let isTopLevelPluginSelected = selection.instanceID.map(self.isEnabledTopLevelUserPlugin) ?? false\n        let selectedProvider = if isOverviewSelected {\n            self.resolvedMenuProvider(enabledProviders: enabledProviders)\n        } else if isTopLevelPluginSelected {\n            nil\n        } else {\n            selection.provider\n        }\n        let currentProvider = selectedProvider ?? enabledProviders.first ?? .codex\n        let suppressProviderSpecificChrome = isOverviewSelected || isTopLevelPluginSelected\n        let codexAccountDisplay = suppressProviderSpecificChrome\n            ? nil\n            : self.codexAccountMenuDisplay(for: currentProvider)\n        let tokenAccountDisplay = suppressProviderSpecificChrome\n            ? nil\n            : self.tokenAccountMenuDisplay(for: currentProvider)\n''')
replace_once(path,
'''        let descriptor = self.makeMenuDescriptor(\n            provider: selectedProvider,\n            includeContextualActions: !isOverviewSelected)\n''',
'''        let descriptor = self.makeMenuDescriptor(\n            provider: selectedProvider,\n            includeContextualActions: !suppressProviderSpecificChrome)\n''')

# Docs.
path = "docs/plugins.md"
replace_once(path,
'''- `name`: trimmed display name, 1–80 UTF-8 bytes.\n''',
'''- `name`: trimmed display name, 1–80 UTF-8 bytes.\n- `topLevel` (optional, default `false`): when `true`, an enabled user plugin appears as its own tab in the merged\n  provider switcher instead of being appended beneath every built-in provider tab. This is presentation-only and does\n  not expand the plugin's sandbox authority or approval binding.\n''')

# Focused tests: manifest parsing and switcher composition.
test_path = ROOT / "Tests/CodexBarTests/UserPluginTopLevelTests.swift"
test_path.write_text(r'''#if canImport(JavaScriptCore)
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
            onSelect: { _ in })

        #expect(view._test_segmentSelections() == [
            .provider(UsageProvider.codex.instanceID),
            .provider(pluginID),
        ])
    }
}
#endif
''')

print("Applied top-level user plugin tab support")
