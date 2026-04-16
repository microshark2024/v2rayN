"""Global constants and configuration for v2rayN.

Ported from ServiceLib/Global.cs - contains all application-wide constants,
URL templates, protocol definitions, and static configuration lists.
"""

from __future__ import annotations

from v2rayn.enums.config_type import EConfigType
from v2rayn.enums.core_type import ECoreType

# ============================================================================
# Application Constants
# ============================================================================

APP_NAME = "v2rayN"
GITHUB_URL = "https://github.com"
GITHUB_API_URL = "https://api.github.com/repos"
GEO_URL = "https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/{0}.dat"
SINGBOX_RULESET_URL = "https://raw.githubusercontent.com/2dust/sing-box-rules/rule-set-{0}/{1}.srs"

PROMOTION_URL = "aHR0cHM6Ly85LjIzNDQ1Ni54eXovYWJjLmh0bWw="

# ============================================================================
# File Names
# ============================================================================

CONFIG_FILE_NAME = "guiNConfig.json"
CORE_CONFIG_FILE_NAME = "config.json"
CORE_PRE_CONFIG_FILE_NAME = "configPre.json"
CORE_SPEEDTEST_CONFIG_FILE_NAME = "configTest{0}.json"
CLASH_MIXIN_CONFIG_FILE_NAME = "Mixin.yaml"

# ============================================================================
# Resource Namespace / Sample Names
# ============================================================================

NAMESPACE_SAMPLE = "ServiceLib.Sample."
V2RAY_SAMPLE_CLIENT = NAMESPACE_SAMPLE + "SampleClientConfig"
SINGBOX_SAMPLE_CLIENT = NAMESPACE_SAMPLE + "SingboxSampleClientConfig"
V2RAY_SAMPLE_HTTP_REQUEST_FILE_NAME = NAMESPACE_SAMPLE + "SampleHttpRequest"
V2RAY_SAMPLE_HTTP_RESPONSE_FILE_NAME = NAMESPACE_SAMPLE + "SampleHttpResponse"
V2RAY_SAMPLE_INBOUND = NAMESPACE_SAMPLE + "SampleInbound"
V2RAY_SAMPLE_OUTBOUND = NAMESPACE_SAMPLE + "SampleOutbound"
SINGBOX_SAMPLE_OUTBOUND = NAMESPACE_SAMPLE + "SingboxSampleOutbound"
CUSTOM_ROUTING_FILE_NAME = NAMESPACE_SAMPLE + "custom_routing_"
TUN_SINGBOX_DNS_FILE_NAME = NAMESPACE_SAMPLE + "tun_singbox_dns"
TUN_SINGBOX_INBOUND_FILE_NAME = NAMESPACE_SAMPLE + "tun_singbox_inbound"
TUN_SINGBOX_RULES_FILE_NAME = NAMESPACE_SAMPLE + "tun_singbox_rules"
DNS_V2RAY_NORMAL_FILE_NAME = NAMESPACE_SAMPLE + "dns_v2ray_normal"
DNS_SINGBOX_NORMAL_FILE_NAME = NAMESPACE_SAMPLE + "dns_singbox_normal"
CLASH_MIXIN_YAML = NAMESPACE_SAMPLE + "clash_mixin_yaml"
CLASH_TUN_YAML = NAMESPACE_SAMPLE + "clash_tun_yaml"
LINUX_AUTOSTART_CONFIG = NAMESPACE_SAMPLE + "linux_autostart_config"
PAC_FILE_NAME = NAMESPACE_SAMPLE + "pac"
PROXY_SET_OSX_SHELL_FILE_NAME = NAMESPACE_SAMPLE + "proxy_set_osx_sh"
PROXY_SET_LINUX_SHELL_FILE_NAME = NAMESPACE_SAMPLE + "proxy_set_linux_sh"
KILL_AS_SUDO_OSX_SHELL_FILE_NAME = NAMESPACE_SAMPLE + "kill_as_sudo_osx_sh"
KILL_AS_SUDO_LINUX_SHELL_FILE_NAME = NAMESPACE_SAMPLE + "kill_as_sudo_linux_sh"
SINGBOX_FAKEIP_FILTER_FILE_NAME = NAMESPACE_SAMPLE + "singbox_fakeip_filter"

# ============================================================================
# Protocol / Network Constants
# ============================================================================

DEFAULT_SECURITY = "auto"
DEFAULT_NETWORK = "tcp"
TCP_HEADER_HTTP = "http"
NONE = "none"
PROXY_TAG = "proxy"
DIRECT_TAG = "direct"
BLOCK_TAG = "block"
DNS_TAG = "dns-module"
DIRECT_DNS_TAG = "direct-dns"
BALANCER_TAG_SUFFIX = "-round"
STREAM_SECURITY = "tls"
STREAM_SECURITY_REALITY = "reality"
LOOPBACK = "127.0.0.1"
INBOUND_API_PROTOCOL = "dokodemo-door"
HTTP_PROTOCOL = "http://"
HTTPS_PROTOCOL = "https://"
SOCKS_PROTOCOL = "socks://"
SOCKS5_PROTOCOL = "socks5://"
AS_IS = "AsIs"
IP_IF_NON_MATCH = "IPIfNonMatch"
IP_ON_DEMAND = "IPOnDemand"

USER_EMAIL = "t@t.tt"
AUTO_RUN_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTO_RUN_NAME = "v2rayNAutoRun"
SYSTEM_PROXY_EXCEPTIONS_WINDOWS = (
    "localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;"
    "172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;"
    "172.28.*;172.29.*;172.30.*;172.31.*;192.168.*"
)
SYSTEM_PROXY_EXCEPTIONS_LINUX = "localhost,127.0.0.0/8,::1"
ROUTING_RULE_COMMA = "<COMMA>"
GRPC_GUN_MODE = "gun"
GRPC_MULTI_MODE = "multi"
MAX_PORT = 65536
MIN_FONT_SIZE = 8
MIN_FONT_SIZE_COUNT = 13
REBOOT_AS = "rebootas"
AVA_ASSETS = "avares://v2rayN/Assets/"
LOCAL_APP_DATA = "V2RAYN_LOCAL_APPLICATION_DATA_V2"
V2RAY_LOCAL_ASSET = "V2RAY_LOCATION_ASSET"
XRAY_LOCAL_ASSET = "XRAY_LOCATION_ASSET"
XRAY_LOCAL_CERT = "XRAY_LOCATION_CERT"
SPEED_TEST_PAGE_SIZE = 1000
LINUX_BASH = "/bin/bash"

# ============================================================================
# Singbox DNS Tags
# ============================================================================

SINGBOX_DIRECT_DNS_TAG = "direct_dns"
SINGBOX_REMOTE_DNS_TAG = "remote_dns"
SINGBOX_LOCAL_DNS_TAG = "local_local"
SINGBOX_HOSTS_DNS_TAG = "hosts_dns"
SINGBOX_FAKE_DNS_TAG = "fake_dns"

HYSTERIA2_DEFAULT_HOP_INT = 10

# ============================================================================
# Policy Group Filters
# ============================================================================

POLICY_GROUP_EXCLUDE_KEYWORDS = r"剩余|过期|到期|重置|[Rr]emaining|[Ee]xpir|[Rr]eset"
POLICY_GROUP_DEFAULT_ALL_FILTER = f"^(?!.*(?:{POLICY_GROUP_EXCLUDE_KEYWORDS})).*$"

POLICY_GROUP_DEFAULT_FILTER_LIST: list[str] = [
    # All nodes (exclude traffic/expiry info)
    POLICY_GROUP_DEFAULT_ALL_FILTER,
    # Low multiplier nodes, e.g. ×0.1, 0.5x, 0.1倍
    r"^.*(?:[×xX✕*]\s*0\.[0-9]+|0\.[0-9]+\s*[×xX✕*倍]).*$",
    # Dedicated line nodes, e.g. IPLC, IEPL
    f"^(?!.*(?:{POLICY_GROUP_EXCLUDE_KEYWORDS})).*(?:专线|IPLC|IEPL|中转).*$",
    # Japan nodes
    f"^(?!.*(?:{POLICY_GROUP_EXCLUDE_KEYWORDS})).*(?:日本|\\b[Jj][Pp]\\b|🇯🇵|[Jj]apan).*$",
]

# ============================================================================
# Protocol Share URLs
# ============================================================================

HYSTERIA2_PROTOCOL_SHARE = "hy2://"
NAIVE_HTTPS_PROTOCOL_SHARE = "naive+https://"
NAIVE_QUIC_PROTOCOL_SHARE = "naive+quic://"

PROTOCOL_SHARES: dict[EConfigType, str] = {
    EConfigType.VMess: "vmess://",
    EConfigType.Shadowsocks: "ss://",
    EConfigType.SOCKS: "socks://",
    EConfigType.VLESS: "vless://",
    EConfigType.Trojan: "trojan://",
    EConfigType.Hysteria2: "hysteria2://",
    EConfigType.TUIC: "tuic://",
    EConfigType.WireGuard: "wireguard://",
    EConfigType.Anytls: "anytls://",
    EConfigType.Naive: "naive://",
}

PROTOCOL_TYPES: dict[EConfigType, str] = {
    EConfigType.VMess: "vmess",
    EConfigType.Shadowsocks: "shadowsocks",
    EConfigType.SOCKS: "socks",
    EConfigType.HTTP: "http",
    EConfigType.VLESS: "vless",
    EConfigType.Trojan: "trojan",
    EConfigType.Hysteria2: "hysteria2",
    EConfigType.TUIC: "tuic",
    EConfigType.WireGuard: "wireguard",
    EConfigType.Anytls: "anytls",
    EConfigType.Naive: "naive",
}

# ============================================================================
# Security / Encryption Lists
# ============================================================================

VMESS_SECURITIES: list[str] = [
    "aes-128-gcm",
    "chacha20-poly1305",
    "auto",
    "none",
    "zero",
]

SS_SECURITIES: list[str] = [
    "aes-256-gcm",
    "aes-128-gcm",
    "chacha20-poly1305",
    "chacha20-ietf-poly1305",
    "none",
    "plain",
]

SS_SECURITIES_IN_XRAY: list[str] = [
    "aes-256-gcm",
    "aes-128-gcm",
    "chacha20-poly1305",
    "chacha20-ietf-poly1305",
    "xchacha20-poly1305",
    "xchacha20-ietf-poly1305",
    "none",
    "plain",
    "2022-blake3-aes-128-gcm",
    "2022-blake3-aes-256-gcm",
    "2022-blake3-chacha20-poly1305",
]

SS_SECURITIES_IN_SINGBOX: list[str] = [
    "aes-256-gcm",
    "aes-192-gcm",
    "aes-128-gcm",
    "chacha20-ietf-poly1305",
    "xchacha20-ietf-poly1305",
    "none",
    "2022-blake3-aes-128-gcm",
    "2022-blake3-aes-256-gcm",
    "2022-blake3-chacha20-poly1305",
    "aes-128-ctr",
    "aes-192-ctr",
    "aes-256-ctr",
    "aes-128-cfb",
    "aes-192-cfb",
    "aes-256-cfb",
    "rc4-md5",
    "chacha20-ietf",
    "xchacha20",
]

FLOWS: list[str] = [
    "",
    "xtls-rprx-vision",
    "xtls-rprx-vision-udp443",
]

NETWORKS: list[str] = [
    "tcp",
    "kcp",
    "ws",
    "httpupgrade",
    "xhttp",
    "h2",
    "quic",
    "grpc",
]

KCP_HEADER_TYPES: list[str] = [
    "srtp",
    "utp",
    "wechat-video",
    "dtls",
    "wireguard",
    "dns",
]

KCP_HEADER_MASK_MAP: dict[str, str] = {
    "srtp": "header-srtp",
    "utp": "header-utp",
    "wechat-video": "header-wechat",
    "dtls": "header-dtls",
    "wireguard": "header-wireguard",
    "dns": "header-dns",
}

CORE_TYPES: list[str] = [
    "Xray",
    "sing_box",
]

XRAY_SUPPORT_CONFIG_TYPE: set[EConfigType] = {
    EConfigType.VMess,
    EConfigType.VLESS,
    EConfigType.Shadowsocks,
    EConfigType.Trojan,
    EConfigType.Hysteria2,
    EConfigType.WireGuard,
    EConfigType.SOCKS,
    EConfigType.HTTP,
}

SINGBOX_SUPPORT_CONFIG_TYPE: set[EConfigType] = {
    EConfigType.VMess,
    EConfigType.VLESS,
    EConfigType.Shadowsocks,
    EConfigType.Trojan,
    EConfigType.Hysteria2,
    EConfigType.TUIC,
    EConfigType.Anytls,
    EConfigType.Naive,
    EConfigType.WireGuard,
    EConfigType.SOCKS,
    EConfigType.HTTP,
}

SINGBOX_ONLY_CONFIG_TYPE: set[EConfigType] = SINGBOX_SUPPORT_CONFIG_TYPE - XRAY_SUPPORT_CONFIG_TYPE

DOMAIN_STRATEGIES: list[str] = [
    AS_IS,
    IP_IF_NON_MATCH,
    IP_ON_DEMAND,
]

DOMAIN_STRATEGIES_4SBOX: list[str] = [
    "",
    "prefer_ipv4",
    "prefer_ipv6",
    "ipv4_only",
    "ipv6_only",
]

FINGERPRINTS: list[str] = [
    "chrome",
    "firefox",
    "safari",
    "ios",
    "android",
    "edge",
    "360",
    "qq",
    "random",
    "randomized",
    "",
]

USER_AGENT: list[str] = [
    "chrome",
    "firefox",
    "safari",
    "edge",
    "none",
]

XHTTP_MODE: list[str] = [
    "auto",
    "packet-up",
    "stream-up",
    "stream-one",
]

ALLOW_INSECURE: list[str] = [
    "true",
    "false",
    "",
]

DOMAIN_STRATEGY: list[str] = [
    "AsIs",
    "UseIP",
    "UseIPv4v6",
    "UseIPv6v4",
    "UseIPv4",
    "UseIPv6",
    "",
]

DOMAIN_DIRECT_DNS_ADDRESS: list[str] = [
    "https://dns.alidns.com/dns-query",
    "https://doh.pub/dns-query",
    "https://dns.alidns.com/dns-query,https://doh.pub/dns-query",
    "223.5.5.5",
    "119.29.29.29",
    "localhost",
]

DOMAIN_REMOTE_DNS_ADDRESS: list[str] = [
    "https://cloudflare-dns.com/dns-query",
    "https://dns.google/dns-query",
    "https://cloudflare-dns.com/dns-query,https://dns.google/dns-query,8.8.8.8",
    "https://dns.cloudflare.com/dns-query",
    "https://doh.dns.sb/dns-query",
    "https://doh.opendns.com/dns-query",
    "https://common.dot.dns.yandex.net",
    "8.8.8.8",
    "1.1.1.1",
    "185.222.222.222",
    "208.67.222.222",
    "77.88.8.8",
]

DOMAIN_PURE_IP_DNS_ADDRESS: list[str] = [
    "223.5.5.5",
    "119.29.29.29",
    "localhost",
]

LANGUAGES: list[str] = [
    "zh-Hans",
    "zh-Hant",
    "en",
    "fa-Ir",
    "fr",
    "ru",
    "hu",
]

ALPNS: list[str] = [
    "h3",
    "h2",
    "http/1.1",
    "h3,h2",
    "h2,http/1.1",
    "h3,h2,http/1.1",
    "",
]

LOG_LEVELS: list[str] = [
    "debug",
    "info",
    "warning",
    "error",
    "none",
]

LOG_LEVEL_COLORS: dict[str, str] = {
    "debug": "#6C757D",
    "info": "#2ECC71",
    "warning": "#FFA500",
    "error": "#E74C3C",
}

INBOUND_TAGS: list[str] = [
    "socks",
    "socks2",
    "socks3",
]

RULE_PROTOCOLS: list[str] = [
    "http",
    "tls",
    "bittorrent",
]

RULE_NETWORKS: list[str] = [
    "",
    "tcp",
    "udp",
    "tcp,udp",
]

DEST_OVERRIDE_PROTOCOLS: list[str] = [
    "http",
    "tls",
    "quic",
    "fakedns",
    "fakedns+others",
]

TUN_MTUS: list[int] = [
    1280,
    1408,
    1500,
    4064,
    9000,
    65535,
]

TUN_STACKS: list[str] = [
    "gvisor",
    "system",
    "mixed",
]

PRESET_MSG_FILTERS: list[str] = [
    "proxy",
    "direct",
    "block",
    "",
]

SINGBOX_MUXS: list[str] = [
    "h2mux",
    "smux",
    "yamux",
    "",
]

TUIC_CONGESTION_CONTROLS: list[str] = [
    "cubic",
    "new_reno",
    "bbr",
]

NAIVE_CONGESTION_CONTROLS: list[str] = [
    "bbr",
    "bbr2",
    "cubic",
    "reno",
]

ALLOW_SELECT_TYPE: list[str] = [
    "selector",
    "urltest",
    "loadbalance",
    "fallback",
]

NOT_ALLOW_TEST_TYPE: list[str] = [
    "selector",
    "urltest",
    "direct",
    "reject",
    "compatible",
    "pass",
    "loadbalance",
    "fallback",
]

PROXY_VEHICLE_TYPE: list[str] = [
    "file",
    "http",
]

# ============================================================================
# IE Proxy Protocol Templates
# ============================================================================

IE_PROXY_PROTOCOLS: list[str] = [
    "{ip}:{http_port}",
    "socks={ip}:{socks_port}",
    "http={ip}:{http_port};https={ip}:{http_port};ftp={ip}:{http_port};socks={ip}:{socks_port}",
    "http=http://{ip}:{http_port};https=http://{ip}:{http_port}",
    "",
]

# ============================================================================
# Subscription Convert URLs
# ============================================================================

SUB_CONVERT_URLS: list[str] = [
    "https://sub.xeton.dev/sub?url={0}",
    "https://api.dler.io/sub?url={0}",
    "http://127.0.0.1:25500/sub?url={0}",
    "",
]

SUB_CONVERT_CONFIG: list[str] = [
    "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online.ini",
]

SUB_CONVERT_TARGETS: list[str] = [
    "",
    "mixed",
    "v2ray",
    "clash",
    "ss",
]

# ============================================================================
# Speed Test URLs
# ============================================================================

SPEED_TEST_URLS: list[str] = [
    "https://cachefly.cachefly.net/50mb.test",
    "https://speed.cloudflare.com/__down?bytes=10000000",
    "https://speed.cloudflare.com/__down?bytes=50000000",
    "https://speed.cloudflare.com/__down?bytes=100000000",
]

SPEED_PING_TEST_URLS: list[str] = [
    "https://www.google.com/generate_204",
    "https://www.gstatic.com/generate_204",
    "https://www.apple.com/library/test/success.html",
    "http://www.msftconnecttest.com/connecttest.txt",
]

# ============================================================================
# Geo File Sources
# ============================================================================

GEO_FILES_SOURCES: list[str] = [
    "",
    "https://github.com/runetfreedom/russia-v2ray-rules-dat/releases/latest/download/{0}.dat",
    "https://github.com/Chocolate4U/Iran-v2ray-rules/releases/latest/download/{0}.dat",
]

SINGBOX_RULESET_SOURCES: list[str] = [
    "",
    "https://raw.githubusercontent.com/runetfreedom/russia-v2ray-rules-dat/release/sing-box/rule-set-{0}/{1}.srs",
    "https://raw.githubusercontent.com/chocolate4u/Iran-sing-box-rules/rule-set/{1}.srs",
]

ROUTING_RULES_SOURCES: list[str] = [
    "",
    "https://raw.githubusercontent.com/runetfreedom/russia-v2ray-custom-routing-list/main/v2rayN/template.json",
    "https://raw.githubusercontent.com/Chocolate4U/Iran-v2ray-rules/main/v2rayN/template.json",
]

DNS_TEMPLATE_SOURCES: list[str] = [
    "",
    "https://raw.githubusercontent.com/runetfreedom/russia-v2ray-custom-routing-list/main/v2rayN/",
    "https://raw.githubusercontent.com/Chocolate4U/Iran-v2ray-rules/main/v2rayN/",
]

# ============================================================================
# User Agent Texts
# ============================================================================

USER_AGENT_TEXTS: dict[str, str] = {
    "chrome": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
    ),
    "firefox": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
    ),
    "safari": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    ),
    "edge": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70"
    ),
    "none": "",
}

# ============================================================================
# Core URLs (GitHub repos)
# ============================================================================

CORE_URLS: dict[ECoreType, str] = {
    ECoreType.v2fly: "v2fly/v2ray-core",
    ECoreType.v2fly_v5: "v2fly/v2ray-core",
    ECoreType.Xray: "XTLS/Xray-core",
    ECoreType.sing_box: "SagerNet/sing-box",
    ECoreType.mihomo: "MetaCubeX/mihomo",
    ECoreType.hysteria: "apernet/hysteria",
    ECoreType.hysteria2: "apernet/hysteria",
    ECoreType.naiveproxy: "klzgrad/naiveproxy",
    ECoreType.tuic: "EAimTY/tuic",
    ECoreType.juicity: "juicity/juicity",
    ECoreType.brook: "txthinking/brook",
    ECoreType.overtls: "ShadowsocksR-Live/overtls",
    ECoreType.shadowquic: "spongebob888/shadowquic",
    ECoreType.mieru: "enfein/mieru",
    ECoreType.v2rayN: "2dust/v2rayN",
}

# ============================================================================
# Other Geo URLs
# ============================================================================

OTHER_GEO_URLS: list[str] = [
    "https://raw.githubusercontent.com/Loyalsoldier/geoip/release/geoip-only-cn-private.dat",
    "https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb",
    "https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/geoip.metadb",
]

# ============================================================================
# IP API URLs
# ============================================================================

IP_API_URLS: list[str] = [
    "https://api.ip.sb/geoip",
    "https://api-ipv4.ip.sb/geoip",
    "https://api-ipv6.ip.sb/geoip",
    "https://api.ipapi.is",
    "",
]

OUTBOUND_TAGS: list[str] = [
    PROXY_TAG,
    DIRECT_TAG,
    BLOCK_TAG,
]

# ============================================================================
# Predefined DNS Hosts
# ============================================================================

PREDEFINED_HOSTS: dict[str, list[str]] = {
    "dns.google": ["8.8.8.8", "8.8.4.4", "2001:4860:4860::8888", "2001:4860:4860::8844"],
    "dns.alidns.com": ["223.5.5.5", "223.6.6.6", "2400:3200::1", "2400:3200:baba::1"],
    "one.one.one.one": ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001"],
    "1dot1dot1dot1.cloudflare-dns.com": [
        "1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001",
    ],
    "cloudflare-dns.com": [
        "104.16.249.249", "104.16.248.249", "2606:4700::6810:f8f9", "2606:4700::6810:f9f9",
    ],
    "dns.cloudflare.com": [
        "104.16.132.229", "104.16.133.229", "2606:4700::6810:84e5", "2606:4700::6810:85e5",
    ],
    "dot.pub": ["1.12.12.12", "120.53.53.53"],
    "doh.pub": ["1.12.12.12", "120.53.53.53"],
    "dns.quad9.net": ["9.9.9.9", "149.112.112.112", "2620:fe::fe", "2620:fe::9"],
    "dns.yandex.net": [
        "77.88.8.8", "77.88.8.1", "2a02:6b8::feed:0ff", "2a02:6b8:0:1::feed:0ff",
    ],
    "dns.sb": ["185.222.222.222", "2a09::"],
    "dns.umbrella.com": [
        "208.67.220.220", "208.67.222.222", "2620:119:35::35", "2620:119:53::53",
    ],
    "dns.sse.cisco.com": [
        "208.67.220.220", "208.67.222.222", "2620:119:35::35", "2620:119:53::53",
    ],
    "engage.cloudflareclient.com": ["162.159.192.1"],
}

EXPECTED_IPS: list[str] = [
    "geoip:cn",
    "geoip:ir",
    "geoip:ru",
    "",
]

ECH_FORCE_QUERYS: list[str] = [
    "none",
    "half",
    "full",
    "",
]

TUN_ICMP_ROUTING_POLICIES: list[str] = [
    "rule",
    "direct",
    "unreachable",
    "drop",
    "reply",
]
