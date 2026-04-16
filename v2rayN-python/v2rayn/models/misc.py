"""Miscellaneous models.

Ported from various ServiceLib/Models/*.cs files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.core_type import ECoreType


@dataclass
class CheckUpdateModel:
    """Check update display model.

    Ported from ServiceLib/Models/CheckUpdateModel.cs.
    """

    is_selected: bool | None = None
    core_type: str | None = None
    remarks: str | None = None
    file_name: str | None = None
    is_finished: bool | None = None


@dataclass
class CmdItem:
    """Command item.

    Ported from ServiceLib/Models/CmdItem.cs.
    """

    cmd: str | None = None
    arguments: list[str] | None = None


@dataclass
class ComboItem:
    """Combo box item.

    Ported from ServiceLib/Models/ComboItem.cs.
    """

    id: str | None = None
    text: str | None = None


@dataclass
class CoreInfo:
    """Core binary info.

    Ported from ServiceLib/Models/CoreInfo.cs.
    """

    core_type: ECoreType = ECoreType.Xray
    core_exes: list[str] | None = None
    arguments: str | None = None
    url: str | None = None
    release_api_url: str | None = None
    download_url_win64: str | None = None
    download_url_win_arm64: str | None = None
    download_url_linux64: str | None = None
    download_url_linux_arm64: str | None = None
    download_url_osx64: str | None = None
    download_url_osx_arm64: str | None = None
    match: str | None = None
    version_arg: str | None = None
    absolute_path: bool = False
    environment: dict[str, str | None] = field(default_factory=dict)


@dataclass
class GitHubReleaseAsset:
    """GitHub release asset.

    Ported from ServiceLib/Models/GitHubRelease.cs.
    """

    url: str | None = None
    id: int = 0
    node_id: str | None = None
    name: str | None = None
    label: object = None
    content_type: str | None = None
    state: str | None = None
    size: int = 0
    download_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    browser_download_url: str | None = None


@dataclass
class GitHubRelease:
    """GitHub release.

    Ported from ServiceLib/Models/GitHubRelease.cs.
    """

    url: str | None = None
    assets_url: str | None = None
    upload_url: str | None = None
    html_url: str | None = None
    id: int = 0
    node_id: str | None = None
    tag_name: str | None = None
    target_commitish: str | None = None
    name: str | None = None
    draft: bool = False
    prerelease: bool = False
    created_at: datetime | None = None
    published_at: datetime | None = None
    assets: list[GitHubReleaseAsset] = field(default_factory=list)
    tarball_url: str | None = None
    zipball_url: str | None = None
    body: str | None = None


@dataclass
class IPAPIInfo:
    """IP API info.

    Ported from ServiceLib/Models/IPAPIInfo.cs.
    """

    ip: str | None = None
    client_ip: str | None = None
    ip_addr: str | None = None
    query: str | None = None
    country: str | None = None
    country_name: str | None = None
    country_code: str | None = None
    location: LocationInfo | None = None


@dataclass
class LocationInfo:
    """Location info."""

    country_code: str | None = None


@dataclass
class RetResult:
    """Operation return result.

    Ported from ServiceLib/Models/RetResult.cs.
    """

    success: bool = False
    msg: str | None = None
    data: object | None = None

    def __init__(
        self,
        success: bool = False,
        msg: str | None = None,
        data: object | None = None,
    ):
        self.success = success
        self.msg = msg
        self.data = data


@dataclass
class SemanticVersion:
    """Semantic version for comparing versions.

    Ported from ServiceLib/Models/SemanticVersion.cs.
    """

    major: int = 0
    minor: int = 0
    patch: int = 0

    def __init__(self, version: str | None = None, major: int = 0, minor: int = 0, patch: int = 0):
        if version is not None:
            self._parse(version)
        else:
            self.major = major
            self.minor = minor
            self.patch = patch

    def _parse(self, version: str) -> None:
        """Parse version string."""
        try:
            if not version:
                self.major = self.minor = self.patch = 0
                return

            version = version.lstrip("v")
            parts = version.split(".")

            if len(parts) == 2:
                self.major = int(parts[0])
                self.minor = int(parts[1])
                self.patch = 0
            elif len(parts) in (3, 4):
                self.major = int(parts[0])
                self.minor = int(parts[1])
                self.patch = int(parts[2])
            else:
                raise ValueError("Invalid version string")
        except (ValueError, IndexError):
            self.major = self.minor = self.patch = 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self.major == other.major and self.minor == other.minor and self.patch == other.patch

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch))

    def __ge__(self, other: SemanticVersion) -> bool:
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        return self.patch >= other.patch

    def __le__(self, other: SemanticVersion) -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch <= other.patch

    def __gt__(self, other: SemanticVersion) -> bool:
        return self >= other and self != other

    def __lt__(self, other: SemanticVersion) -> bool:
        return self <= other and self != other

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def to_version_string(self, prefix: str | None = None) -> str:
        """Get version string with optional prefix."""
        v = str(self)
        return f"{prefix}{v}" if prefix else v


@dataclass
class ServerStatItem:
    """Server statistics item.

    Ported from ServiceLib/Models/ServerStatItem.cs.
    """

    index_id: str = ""
    total_up: int = 0
    total_down: int = 0
    today_up: int = 0
    today_down: int = 0
    date_now: int = 0


@dataclass
class ServerSpeedItem(ServerStatItem):
    """Server speed item.

    Ported from ServiceLib/Models/ServerSpeedItem.cs.
    """

    proxy_up: int = 0
    proxy_down: int = 0
    direct_up: int = 0
    direct_down: int = 0


@dataclass
class TrafficItem:
    """Traffic item."""

    up: int = 0
    down: int = 0


@dataclass
class ServerTestItem:
    """Server test item.

    Ported from ServiceLib/Models/ServerTestItem.cs.
    """

    index_id: str | None = None
    address: str | None = None
    port: int = 0
    config_type: EConfigType = EConfigType.VMess
    allow_test: bool = False
    queue_num: int = 0
    profile: object | None = None  # ProfileItem
    core_type: ECoreType = ECoreType.Xray


@dataclass
class SpeedTestResult:
    """Speed test result.

    Ported from ServiceLib/Models/SpeedTestResult.cs.
    """

    index_id: str | None = None
    delay: str | None = None
    speed: str | None = None


@dataclass
class UpdateResult:
    """Update check result.

    Ported from ServiceLib/Models/UpdateResult.cs.
    """

    success: bool = False
    msg: str | None = None
    version: SemanticVersion | None = None
    url: str | None = None


@dataclass
class VmessQRCode:
    """VMess QR code data.

    Ported from ServiceLib/Models/VmessQRCode.cs.
    """

    v: int = 2
    ps: str = ""
    add: str = ""
    port: int = 0
    id: str = ""
    aid: int = 0
    scy: str = ""
    net: str = ""
    type: str = ""
    host: str = ""
    path: str = ""
    tls: str = ""
    sni: str = ""
    alpn: str = ""
    fp: str = ""
    insecure: str = ""


@dataclass
class SsServer:
    """Shadowsocks SIP008 server.

    Ported from ServiceLib/Models/SsSIP008.cs.
    """

    remarks: str | None = None
    server: str | None = None
    server_port: str | None = None
    method: str | None = None
    password: str | None = None
    plugin: str | None = None


@dataclass
class SsSIP008:
    """Shadowsocks SIP008 configuration."""

    servers: list[SsServer] | None = None


@dataclass
class CoreConfigContext:
    """Core configuration build context.

    Ported from ServiceLib/Models/CoreConfigContext.cs.
    """

    node: object = None  # ProfileItem
    run_core_type: ECoreType = ECoreType.Xray
    routing_item: object | None = None  # RoutingItem
    raw_dns_item: object | None = None  # DNSItem
    simple_dns_item: object = field(default_factory=dict)
    all_proxies_map: dict[str, object] = field(default_factory=dict)
    app_config: object = field(default_factory=dict)
    full_config_template: object | None = None
    server_test_item_map: dict[str, str] = field(default_factory=dict)
    is_tun_enabled: bool = False
    protect_domain_list: set[str] = field(default_factory=set)
    tun_protect_ss_port: int = 0
    proxy_relay_ss_port: int = 0
