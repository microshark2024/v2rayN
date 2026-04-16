"""View action enum."""

from enum import IntEnum


class EViewAction(IntEnum):
    """View action types for UI interaction."""

    CloseWindow = 0
    ShowYesNo = 1
    SaveFileDialog = 2
    AddBatchRoutingRulesYesNo = 3
    SetClipboardData = 4
    AddServerViaClipboard = 5
    ImportRulesFromClipboard = 6
    ProfilesFocus = 7
    ShareSub = 8
    ShareServer = 9
    ScanScreenTask = 10
    ScanImageTask = 11
    BrowseServer = 12
    ImportRulesFromFile = 13
    InitSettingFont = 14
    PasswordInput = 15
    SubEditWindow = 16
    RoutingRuleSettingWindow = 17
    RoutingRuleDetailsWindow = 18
    AddServerWindow = 19
    AddServer2Window = 20
    AddGroupServerWindow = 21
    DNSSettingWindow = 22
    RoutingSettingWindow = 23
    OptionSettingWindow = 24
    FullConfigTemplateWindow = 25
    GlobalHotkeySettingWindow = 26
    SubSettingWindow = 27
    DispatcherRefreshServersBiz = 28
    DispatcherRefreshIcon = 29
    DispatcherShowMsg = 30
