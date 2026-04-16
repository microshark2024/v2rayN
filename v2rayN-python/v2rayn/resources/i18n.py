"""Internationalization (i18n) support.

Ported from ResUI.Designer.cs (~4791 lines of translation strings).
Uses a simple dictionary-based approach for translations.
"""

from __future__ import annotations

import json
import os
from typing import Any

_current_language = "en"
_translations: dict[str, dict[str, str]] = {}

# Default English strings (subset of the full 4791 lines)
_default_strings = {
    # Main window
    "menuServers": "Servers",
    "menuAddVmessServer": "Add VMess Server",
    "menuAddVlessServer": "Add VLESS Server",
    "menuAddShadowsocksServer": "Add Shadowsocks Server",
    "menuAddSocksServer": "Add SOCKS Server",
    "menuAddTrojanServer": "Add Trojan Server",
    "menuAddHysteria2Server": "Add Hysteria2 Server",
    "menuAddTuicServer": "Add TUIC Server",
    "menuAddWireguardServer": "Add WireGuard Server",
    "menuAddAnytlsServer": "Add Anytls Server",
    "menuImportFromClipboard": "Import from Clipboard",
    "menuImportFromFile": "Import from File",
    "menuExportToClipboard": "Export to Clipboard",
    "menuRemoveSelected": "Remove Selected",
    "menuRemoveDuplicates": "Remove Duplicates",
    "menuSubscription": "Subscription",
    "menuSubSetting": "Subscription Settings",
    "menuSubUpdate": "Update All Subscriptions",
    "menuSubUpdateSelected": "Update Selected Subscription",
    "menuSetting": "Settings",
    "menuOptionSetting": "Option Settings",
    "menuRoutingSetting": "Routing Settings",
    "menuDNSSetting": "DNS Settings",
    "menuRebootAsAdmin": "Reboot as Administrator",
    "menuCheckUpdate": "Check Update",
    "menuUpdateN": "Update v2rayN",
    "menuUpdateCore": "Update Xray Core",
    "menuUpdateSingboxCore": "Update Sing-box Core",
    "menuUpdateMihomoCore": "Update Mihomo Core",
    "menuUpdateGeo": "Update Geo Files",
    "menuHelp": "Help",
    "menuAbout": "About",
    # Status
    "statusReady": "Ready",
    "statusConnected": "Connected",
    "statusDisconnected": "Disconnected",
    "statusConnecting": "Connecting...",
    "statusTesting": "Testing...",
    # Proxy types
    "proxyTypeClear": "Clear System Proxy",
    "proxyTypeSet": "Set System Proxy",
    "proxyTypePac": "Set PAC Proxy",
    "proxyTypeUnchanged": "Keep System Proxy Unchanged",
    # Rule modes
    "ruleModeRule": "Rule Mode",
    "ruleModeDirect": "Direct Mode",
    "ruleModeGlobal": "Global Mode",
    # Buttons
    "btnOK": "OK",
    "btnCancel": "Cancel",
    "btnAdd": "Add",
    "btnRemove": "Remove",
    "btnSave": "Save",
    "btnClose": "Close",
    "btnTest": "Test",
    "btnImport": "Import",
    "btnExport": "Export",
    # Dialog labels
    "lblRemarks": "Remarks",
    "lblAddress": "Address",
    "lblPort": "Port",
    "lblPassword": "Password/UUID",
    "lblNetwork": "Network",
    "lblSecurity": "Security",
    "lblSNI": "SNI",
    "lblALPN": "ALPN",
    "lblFingerprint": "Fingerprint",
    "lblHost": "Host",
    "lblPath": "Path",
    "lblHeaderType": "Header Type",
    "lblAllowInsecure": "Allow Insecure",
    # Messages
    "msgConfirmRemove": "Confirm removal of selected items?",
    "msgImportSuccess": "Successfully imported {0} servers",
    "msgImportFail": "Import failed",
    "msgSubscriptionUpdateSuccess": "Subscription updated: {0} servers",
    "msgSubscriptionUpdateFail": "Failed to update subscription",
    "msgTestComplete": "Test complete",
    "msgUpdateAvailable": "New version available: {0}",
    "msgAlreadyLatest": "Already using the latest version",
    "msgSaveSuccess": "Saved successfully",
    "msgSaveFail": "Failed to save",
}


def get_string(key: str, *args: Any) -> str:
    """Get a translated string.

    Args:
        key: Translation key
        *args: Format arguments

    Returns:
        Translated string
    """
    # Try current language first
    if _current_language in _translations:
        text = _translations[_current_language].get(key)
        if text:
            if args:
                try:
                    return text.format(*args)
                except (IndexError, KeyError):
                    return text
            return text

    # Fallback to default
    text = _default_strings.get(key, key)
    if args:
        try:
            return text.format(*args)
        except (IndexError, KeyError):
            return text
    return text


def set_language(language: str) -> None:
    """Set current language.

    Args:
        language: Language code (e.g., 'en', 'zh-CN', 'ja')
    """
    global _current_language
    _current_language = language


def load_translations(file_path: str) -> bool:
    """Load translations from a JSON file.

    Args:
        file_path: Path to translation JSON file

    Returns:
        True on success
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            for lang, strings in data.items():
                if isinstance(strings, dict):
                    _translations[lang] = strings
        return True
    except Exception:
        return False


def get_available_languages() -> list[str]:
    """Get list of available languages."""
    return list(_translations.keys()) or ["en"]


# Convenience alias
_ = get_string
