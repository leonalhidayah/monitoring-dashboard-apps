from datetime import datetime, timedelta
from pathlib import Path

import pytz

DATA_MAP_FINANCE = {
    "Zhi Yang Yao": {
        "Marketplace": [
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "TikTok",
            "Lazada",
            "Lazada",
            "Tokopedia",
            "Tokopedia",
            "Tokopedia",
            "Tokopedia",
        ],
        "Nama Toko": [
            "SP zhi yang yao official store",
            "SP zhi yang yao",
            "SP zhi yang yao official",
            "SP zhi yang yao id",
            "SP zhi yang yao shop",
            "SP zhi yang yao indonesia",
            "SP zhi yang yao mart",
            "SP zhi yang yao store",
            "TT zhi yang yao",
            "LZ zhi yang yao",
            "LZ zhi yang yao id",
            "TP zhi yang yao official store",
            "TP zhi yang yao",
            "TP zhi yang yao store makassar",
            "TP zhi yang yao official medan",
        ],
    },
    "Juwara Herbal": {
        "Marketplace": [
            "Shopee",
            "TikTok",
        ],
        "Nama Toko": [
            "SP juwara herbal official store",
            "TT juwaraherbal",
        ],
    },
    "Enzhico": {
        "Marketplace": [
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "TikTok",
            "Lazada",
            "Lazada",
            "Tokopedia",
        ],
        "Nama Toko": [
            "SP enzhico shop",
            "SP enzhico store",
            "SP enzhico store indonesia",
            "SP enzhico shop indonesia",
            "SP enzhico indonesia",
            "SP enzhico authorize store",
            "SP enzhico",
            "TT enzhico authorized store",
            "LZ enzhico",
            "LZ enzhico store",
            "TP enzhico official store",
        ],
    },
    "Erassgo": {
        "Marketplace": [
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Tokopedia",
            "Lazada",
            "Lazada",
        ],
        "Nama Toko": [
            "SP erassgo official",
            "SP erassgo official store",
            "SP erassgo.co",
            "SP erassgo",
            "SP erassgo makassar",
            "TP erassgo",
            "LZ erassgo",
            "LZ erassgo store id",
        ],
    },
    "Kudaku": {
        "Marketplace": [
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "TikTok",
            "Lazada",
        ],
        "Nama Toko": [
            "SP kudaku",
            "SP kudaku store",
            "SP kudaku official store",
            "SP kudaku id",
            "SP kudaku indonesia",
            "TT kudaku milk",
            "LZ kudaku",
        ],
    },
    "HPI": {
        "Marketplace": [
            "Shopee",
            "TikTok",
        ],
        "Nama Toko": [
            "SP herba pusat indonesia",
            "TT herba pusat indonesia",
        ],
    },
}


ADV_MP_MAP_PROJECT = {
    "Zhi Yang Yao": {
        "Marketplace": [
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Tokopedia",
            "Tokopedia",
            "TikTok",
            "Lazada",
        ],
        "Nama Toko": [
            "SP zhi yang yao official store",
            "SP zhi yang yao official",
            "SP zhi yang yao mart",
            "SP zhi yang yao",
            "SP zhi yang yao (iklan eksternal FB)",
            "TP zhi yang yao official store",
            "TP zhi yang yao",
            "TT zhi yang yao",
            "LZ zhi yang yao",
        ],
    },
    "Juwara Herbal": {
        "Marketplace": [
            "Shopee",
            "TikTok",
        ],
        "Nama Toko": [
            "SP juwara herbal official store",
            "TT juwaraherbal",
        ],
    },
    "Enzhico": {
        "Marketplace": ["Shopee", "Shopee", "Shopee", "TikTok", "Lazada", "Lazada"],
        "Nama Toko": [
            "SP enzhico",
            "SP enzhico store",
            "SP enzhico shop",
            "TT enzhico authorized store",
            "LZ enzhico",
            "LZ enzhico store",
        ],
    },
    "Erassgo": {
        "Marketplace": [
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Tokopedia",
            "Lazada",
            "Lazada",
        ],
        "Nama Toko": [
            "SP erassgo official",
            "SP erassgo official store",
            "SP erassgo.co",
            "SP erassgo",
            "SP erassgo makassar",
            "TP erassgo",
            "LZ erassgo",
            "LZ erassgo store id",
        ],
    },
    "Kudaku": {
        "Marketplace": [
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "Shopee",
            "TikTok",
            "Lazada",
        ],
        "Nama Toko": [
            "SP kudaku",
            "SP kudaku store",
            "SP kudaku official store",
            "SP kudaku id",
            "SP kudaku indonesia",
            "TT kudaku milk",
            "LZ kudaku",
        ],
    },
    "HPI": {
        "Marketplace": [
            "Shopee",
            "TikTok",
        ],
        "Nama Toko": [
            "SP herba pusat indonesia",
            "TT herba pusat indonesia",
        ],
    },
}


ADV_CPAS_MAP_PROJECT = {
    "Zhi Yang Yao": {
        "Nama Toko": [
            "SP zhi yang yao official store",
            "SP zhi yang yao",
            "SP zhi yang yao",
            "TT zhi yang yao",
        ],
        "Akun": [
            "Zhi yang yao mall 1",
            "Zhi yang yao CPAS 03",
            "Zhi yang yao CPAS",
            "Zhi yang yao CPAS Tokopedia",
        ],
    },
    "Enzhico": {
        "Nama Toko": [
            "SP enzhico",
            "TT enzhico authorized store",
        ],
        "Akun": [
            "Enzhico CPAS 1",
            "Enzhico Tokopedia CPAS 1",
        ],
    },
    "Kudaku": {
        "Nama Toko": [
            "SP kudaku official store",
            "TT kudaku milk",
        ],
        "Akun": [
            "Kudaku mall CPAS Shopee",
            "Kudaku milk CPAS Tokopedia",
        ],
    },
    "Erassgo": {
        "Nama Toko": [
            "SP erassgo",
            "SP erassgo official store",
        ],
        "Akun": [
            "Erassgo CPAS 1",
            "Erassgo mall 1",
        ],
    },
}


TOKO_BANDUNG = [
    "SP zhi yang yao official",
    "SP erassgo bandung",
    "SP juwara herbal official store",
    "TT juwara herbal",
]


MARKETPLACE_LIST = ["Lazada", "Shopee", "TikTok", "Tokopedia"]

PROJECT_ROOT = Path().cwd().parent

jakarta_tz = pytz.timezone("Asia/Jakarta")
NOW_IN_JAKARTA = datetime.now(jakarta_tz)
YESTERDAY_IN_JAKARTA = NOW_IN_JAKARTA - timedelta(days=1)

AKUN_REGULAR = [
    "Akun Om Diki",
    "All Akun Sadewa Everpro",
    "All Akun OrderOnline Sadewa",
]

PLATFORM_REGULAR = [
    "Ninja",
    "J&T",
    "Sadewa Citra Mandiri",
]
