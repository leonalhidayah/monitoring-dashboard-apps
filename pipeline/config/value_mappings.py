# Mapping Marketplace
MARKETPLACE_MAP = {
    "Shopee": "SP",
    "Lazada": "LZ",
    "Tokopedia": "TP",
    "TikTok": "TT",
}

# Mapping Brand dari SKU
BRAND_MAP = {
    "ZYY": "Zhi Yang Yao",
    "ERA": "Erassgo",
    "ENZ": "Enzhico",
    "KDK": "Kudaku",
    "JOY": "Joymens",
    "GLU": "Glumevit",
    "GOD": "Godfather",
    "BTN": "Bycetin",
    "BIO": "Bio Antanam",
    "DOU": "Doui",
}

# Mapping Jasa Kirim
SHIPPING_PROVIDER_MAP = {
    # --- SPX (Shopee Express) ---
    "Reguler (Cashless)-SPX Standard": "SPX Standard",
    "SPX Standard": "SPX Standard",
    "Reguler (Cashless)": "SPX Standard",  # fallback kalau kolom tidak detail
    "Hemat Kargo": "SPX Hemat",
    "Hemat Kargo-SPX Hemat": "SPX Hemat",
    # --- Anteraja ---
    "Reguler (Cashless)-Anteraja Reguler": "Anteraja Reguler",
    "Hemat Kargo-Anteraja Economy": "Anteraja Economy",
    # --- SiCepat ---
    "Reguler (Cashless)-SiCepat REG": "SiCepat REG",
    "Hemat Kargo-SiCepat Halu": "SiCepat Halu",
    # --- Ninja Xpress ---
    "Reguler (Cashless)-Ninja Xpress": "Ninja Xpress",
    # --- ID Express ---
    "Reguler (Cashless)-ID Express": "ID Express",
    # --- JNE ---
    "Reguler (Cashless)-JNE Reguler": "JNE Reguler",
    "JNE Reguler": "JNE Reguler",
    "standard": "LEX ID",
}

# Mapping Metode Pembayaran
PAYMENT_METHOD_MAP = {
    # Shopee
    "Online Payment": "E-Wallet / Online Payment",
    "COD (Bayar di Tempat)": "COD",
    "Saldo ShopeePay": "E-Wallet (ShopeePay)",
    "Kartu Kredit/Debit": "Credit/Debit Card",
    "SeaBank Bayar Instan": "Bank Transfer",
    "SPayLater": "PayLater (SPay)",
    # TikTok
    "Bayar di tempat": "COD",
    "Transfer bank": "Bank Transfer",
    "DANA": "E-Wallet (DANA)",
    "OVO": "E-Wallet (OVO)",
    "GoPay": "E-Wallet (GoPay)",
    "QRIS": "QRIS",
    "PayLater": "PayLater (TikTok)",
    "GoPay Later": "PayLater (GoPay)",
    "LinkAja": "E-Wallet (LinkAja)",
    "TikTok Shop Balance": "TikTok Balance",
    "Kartu kredit/debit": "Credit/Debit Card",
    "Cash": "Cash",
    "OVO + TikTok Shop Balance": "E-Wallet (OVO + TikTok Balance)",
}

# Mapping Provinsi
PROVINCES_STANDARD = [
    "Aceh",
    "Sumatera Utara",
    "Sumatera Barat",
    "Riau",
    "Kepulauan Riau",
    "Jambi",
    "Sumatera Selatan",
    "Bangka Belitung",
    "Bengkulu",
    "Lampung",
    "DKI Jakarta",
    "Jawa Barat",
    "Jawa Tengah",
    "DI Yogyakarta",
    "Jawa Timur",
    "Banten",
    "Bali",
    "Nusa Tenggara Barat",
    "Nusa Tenggara Timur",
    "Kalimantan Barat",
    "Kalimantan Tengah",
    "Kalimantan Selatan",
    "Kalimantan Timur",
    "Kalimantan Utara",
    "Sulawesi Utara",
    "Sulawesi Tengah",
    "Sulawesi Selatan",
    "Sulawesi Tenggara",
    "Sulawesi Barat",
    "Gorontalo",
    "Maluku",
    "Maluku Utara",
    "Papua",
    "Papua Barat",
    "Papua Tengah",
    "Papua Pegunungan",
    "Papua Selatan",
    "Papua Barat Daya",
]

PROVINCE_MAPPING = {
    # DKI Jakarta
    "dki jakarta": "DKI Jakarta",
    "jakarta": "DKI Jakarta",
    "jakarta raya": "DKI Jakarta",
    "daerah khusus ibukota jakarta": "DKI Jakarta",
    "jakarta province": "DKI Jakarta",
    # Jawa Barat
    "jawa barat": "Jawa Barat",
    "west java": "Jawa Barat",
    "jabar": "Jawa Barat",
    "java occidental": "Jawa Barat",
    "west java province": "Jawa Barat",
    # Jawa Tengah
    "jawa tengah": "Jawa Tengah",
    "central java": "Jawa Tengah",
    "jateng": "Jawa Tengah",
    # DI Yogyakarta
    "d.i. yogyakarta": "DI Yogyakarta",
    "daerah istimewa yogyakarta": "DI Yogyakarta",
    "yogyakarta": "DI Yogyakarta",
    "diy": "DI Yogyakarta",
    "di yogyakarta": "DI Yogyakarta",
    # Jawa Timur
    "jawa timur": "Jawa Timur",
    "east java": "Jawa Timur",
    "jatim": "Jawa Timur",
    "east java province": "Jawa Timur",
    # Banten
    "banten": "Banten",
    "banten province": "Banten",
    # Bali
    "bali": "Bali",
    "bali province": "Bali",
    # Nusa Tenggara Barat
    "nusa tenggara barat": "Nusa Tenggara Barat",
    "nusa tenggara barat (ntb)": "Nusa Tenggara Barat",
    "ntb": "Nusa Tenggara Barat",
    "'west nusa tenggara": "Nusa Tenggara Barat",
    # Nusa Tenggara Timur
    "nusa tenggara timur": "Nusa Tenggara Timur",
    "nusa tenggara timur (ntt)": "Nusa Tenggara Timur",
    "ntt": "Nusa Tenggara Timur",
    "'east nusa tenggara": "Nusa Tenggara Timur",
    # Sumatera Utara
    "sumatera utara": "Sumatera Utara",
    "north sumatera": "Sumatera Utara",
    "north sumatra province": "Sumatera Utara",
    "sumut": "Sumatera Utara",
    # Sumatera Barat
    "sumatera barat": "Sumatera Barat",
    "west sumatera": "Sumatera Barat",
    "west sumatra": "Sumatera Barat",
    "sumbar": "Sumatera Barat",
    "west sumatra province": "Sumatera Barat",
    # Riau
    "riau": "Riau",
    # Kepulauan Riau
    "kepulauan riau": "Kepulauan Riau",
    "kepri": "Kepulauan Riau",
    "riau islands province": "Kepulauan Riau",
    "riau islands": "Kepulauan Riau",
    # Jambi
    "jambi": "Jambi",
    # Sumatera Selatan
    "sumatera selatan": "Sumatera Selatan",
    "south sumatera": "Sumatera Selatan",
    "sumsel": "Sumatera Selatan",
    "south sumatra": "Sumatera Selatan",
    # Bengkulu
    "bengkulu": "Bengkulu",
    # Bangka Belitung
    "bangka belitung": "Bangka Belitung",
    "kepulauan bangka belitung": "Bangka Belitung",
    "babel": "Bangka Belitung",
    "bangka belitung islands": "Bangka Belitung",
    # Lampung
    "lampung": "Lampung",
    "lampung province": "Lampung",
    # Kalimantan Barat
    "kalimantan barat": "Kalimantan Barat",
    "west kalimantan": "Kalimantan Barat",
    "kalbar": "Kalimantan Barat",
    # Kalimantan Tengah
    "kalimantan tengah": "Kalimantan Tengah",
    "central kalimantan": "Kalimantan Tengah",
    "kalteng": "Kalimantan Tengah",
    "central kalimantan province": "Kalimantan Tengah",
    # Kalimantan Selatan
    "kalimantan selatan": "Kalimantan Selatan",
    "south kalimantan": "Kalimantan Selatan",
    "kalsel": "Kalimantan Selatan",
    # Kalimantan Timur
    "kalimantan timur": "Kalimantan Timur",
    "east kalimantan": "Kalimantan Timur",
    "kaltim": "Kalimantan Timur",
    # Kalimantan Utara
    "kalimantan utara": "Kalimantan Utara",
    "north kalimantan": "Kalimantan Utara",
    "kalut": "Kalimantan Utara",
    # Sulawesi Utara
    "sulawesi utara": "Sulawesi Utara",
    "north sulawesi": "Sulawesi Utara",
    "sulut": "Sulawesi Utara",
    "north sulawesi province": "Sulawesi Utara",
    # Sulawesi Tengah
    "sulawesi tengah": "Sulawesi Tengah",
    "central sulawesi": "Sulawesi Tengah",
    "sulteng": "Sulawesi Tengah",
    # Sulawesi Selatan
    "sulawesi selatan": "Sulawesi Selatan",
    "south sulawesi": "Sulawesi Selatan",
    "sulsel": "Sulawesi Selatan",
    # Sulawesi Tenggara
    "sulawesi tenggara": "Sulawesi Tenggara",
    "southeast sulawesi": "Sulawesi Tenggara",
    "sultra": "Sulawesi Tenggara",
    "southeast sulawesi province": "Sulawesi Tenggara",
    # Sulawesi Barat
    "sulawesi barat": "Sulawesi Barat",
    "west sulawesi": "Sulawesi Barat",
    "sulbar": "Sulawesi Barat",
    # Gorontalo
    "gorontalo": "Gorontalo",
    # Aceh
    "aceh": "Aceh",
    "nanggroe aceh darussalam": "Aceh",
    "nanggroe aceh darussalam (nad)": "Aceh",
    "d.i. aceh": "Aceh",
    # Maluku
    "maluku": "Maluku",
    # Maluku Utara
    "maluku utara": "Maluku Utara",
    "north maluku": "Maluku Utara",
    # Papua
    "papua": "Papua",
    "papua barat": "Papua Barat",
    "west papua": "Papua Barat",
    "papua tengah": "Papua Tengah",
    "central papua": "Papua Tengah",
    "papua pegunungan": "Papua Pegunungan",
    "papua selatan": "Papua Selatan",
    "south papua": "Papua Selatan",
    "papua barat daya": "Papua Barat Daya",
    "southwest papua": "Papua Barat Daya",
}
