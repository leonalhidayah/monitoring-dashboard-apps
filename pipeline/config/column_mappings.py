# BRONZE -> SILVER
SHOPEE_MAP = {
    "No. Pesanan": "Nomor Pesanan",
    "Status Pesanan": "Status Pesanan",
    "No. Resi": "Nomor Resi",
    "Opsi Pengiriman": "Jasa Kirim yang Dipilih Pembeli",
    "Waktu Pesanan Dibuat": "Waktu Pesanan Dibuat",
    "Waktu Pembayaran Dilakukan": "Waktu Pesanan Dibayar",
    "Pesanan Harus Dikirimkan Sebelum (Menghindari keterlambatan)": "Waktu Kedaluwarsa",
    "Waktu Pengiriman Diatur": "Waktu Pesanan Dikirim",
    "Waktu Pesanan Selesai": "Waktu Selesai",
    "Metode Pembayaran": "Metode Pembayaran",
    "Nomor Referensi SKU": "SKU",
    "Nama Produk": "Nama Produk",
    "Harga Awal": "Harga Awal Produk",
    "Harga Setelah Diskon": "Harga Satuan",
    "Jumlah": "Jumlah",
    "Total Harga Produk": "Subtotal Produk",
    "Total Pembayaran": "Total Pesanan",
    "Diskon Dari Penjual": "Diskon Penjual",
    "Diskon Dari Shopee": "Diskon Marketplace",
    "Voucher Ditanggung Penjual": "Voucher Toko",
    "Voucher Ditanggung Shopee": "Voucher",
    "Username (Pembeli)": "Nama Pembeli",
    "Nama Penerima": "Nama Penerima",
    "No. Telepon": "Nomor Telepon",
    "Provinsi": "Provinsi",
    "Kota/Kabupaten": "Kabupaten/Kota",
    "Alamat Pengiriman": "Alamat Lengkap",
    "Catatan dari Pembeli": "Pesan dari Pembeli",
    "Catatan": "Catatan Penjual",
    "Berat Produk": "Berat Produk",
    "Estimasi Potongan Biaya Pengiriman": "Diskon Ongkos Kirim Marketplace",
    "Ongkos Kirim Dibayar oleh Pembeli": "Ongkos Kirim",
    "Sesi Pengiriman": "Sesi Pengiriman",
    "Jenis Resi": "Jenis Resi",
}


TIKTOK_MAP = {
    "Order ID": "Nomor Pesanan",
    "Order Status": "Status Pesanan",
    "Tracking ID": "Nomor Resi",
    "Shipping Provider Name": "Jasa Kirim yang Dipilih Pembeli",
    "Created Time": "Waktu Pesanan Dibuat",
    "Paid Time": "Waktu Pesanan Dibayar",
    "Shipped Time": "Waktu Pesanan Dikirim",
    "Delivered Time": "Waktu Selesai",
    "Payment Method": "Metode Pembayaran",
    "Seller SKU": "SKU",
    "Product Name": "Nama Produk",
    "SKU Unit Original Price": "Harga Awal Produk",
    "Quantity": "Jumlah",
    "SKU Subtotal After Discount": "Subtotal Produk",
    "Order Amount": "Total Pesanan",
    "SKU Seller Discount": "Diskon Penjual",
    "SKU Platform Discount": "Diskon Marketplace",
    "Payment platform discount": "Voucher",
    "Buyer Username": "Nama Pembeli",
    "Recipient": "Nama Penerima",
    "Phone #": "Nomor Telepon",
    "Province": "Provinsi",
    "Regency and City": "Kabupaten/Kota",
    "Detail Address": "Alamat Lengkap",
    "Buyer Message": "Pesan dari Pembeli",
    "Seller Note": "Catatan Penjual",
    "Weight(kg)": "Berat Produk",
    "Shipping Fee Platform Discount": "Diskon Ongkos Kirim Marketplace",
    "Shipping Fee After Discount": "Ongkos Kirim",
    "Sesi Pengiriman": "Sesi Pengiriman",
    "Jenis Resi": "Jenis Resi",
}


# SILVER -> GOLD
# --- DIMENSION MAPS ---
# BRANDS_MAP = {"nama_brand": "nama_brand"}
MARKETPLACES_MAP = {"Marketplace": "nama_marketplace"}
SHIPPING_SERVICES_MAP = {"Jasa Kirim yang Dipilih Pembeli": "jasa_kirim"}
PAYMENT_METHODS_MAP = {"Metode Pembayaran": "metode_pembayaran"}
STORES_MAP = {"Toko Marketplace": "nama_toko_raw", "Marketplace": "nama_marketplace"}
CUSTOMERS_MAP = {
    "Nama Pembeli": "nama_pembeli",
    "Nomor Telepon": "no_telepon",
    "Alamat Lengkap": "alamat_lengkap",
    "Kelurahan": "kelurahan",
    "Kecamatan": "kecamatan",
    "Kabupaten/Kota": "kabupaten_kota",
    "Provinsi": "provinsi",
    "Negara": "negara",
    "Kode Pos": "kode_pos",
}
PRODUCTS_MAP = {
    "SKU": "sku",
    "Nama Produk": "nama_produk",
    "Harga Awal Produk": "harga_awal_produk",
}

# --- FACT MAPS ---
ORDERS_MAP = {
    "Nomor Pesanan": "order_id",
    "Status Pesanan": "order_status",
    "Jenis Resi": "jenis_pesanan",
    "Waktu Pesanan Dibuat": "waktu_pesanan_dibuat",
    "Waktu Pesanan Dibayar": "waktu_pesanan_dibayar",
    "Waktu Kedaluwarsa": "waktu_kadaluwarsa",
    "Waktu Proses": "waktu_proses",
    "Waktu Selesai": "waktu_selesai",
    "Waktu Pembatalan": "waktu_pembatalan",
}
ORDER_ITEMS_MAP = {
    "Nomor Pesanan": "order_id",
    "SKU": "sku",  # Kunci untuk join
    "Jumlah": "jumlah",
    "Harga Satuan": "harga_satuan",
    "Subtotal Produk": "subtotal_produk",
    "Diskon Penjual": "diskon_penjual",
    "Voucher": "voucher",
    "Voucher Toko": "voucher_toko",
}
SHIPMENTS_MAP = {
    "Nomor Pesanan": "order_id",
    "Nomor Resi": "no_resi",
    "Gudang": "gudang_asal",
    "Sesi Pengiriman": "sesi",
    "Ongkos Kirim": "ongkos_kirim",
    "Diskon Ongkos Kirim Penjual": "diskon_ongkos_kirim_penjual",
    "Diskon Ongkos Kirim Marketplace": "diskon_ongkos_kirim_marketplace",
    "Waktu Cetak": "waktu_cetak",
    "Waktu Pesanan Dikirim": "waktu_pesanan_dikirim",
}
PAYMENTS_MAP = {
    "Nomor Pesanan": "order_id",
    "Metode Pembayaran": "metode_pembayaran",  # Kunci untuk join
    "Total Pesanan": "total_pesanan",
    "Biaya Pengelolaan": "biaya_pengelolaan",
    "Biaya Transaksi": "biaya_transaksi",
}

# BRANDS_MAP = {"nama_brand": "nama_brand"}

# MARKETPALCES_MAP = {"Marketplace": "nama_marketplace"}

# SHIPPING_SERVICES_MAP = {
#     "Jasa Kirim yang Dipilih Pembeli": "jasa_kirim",
# }

# PAYMENT_METHODS_MAP = {
#     "Metode Pembayaran": "metode_pembayaran",
# }

# STORES_MAP = {
#     "Toko Marketplace": "nama_toko",
#     "Marketplace": "nama_marketplace",
# }

# CUSTOMERS_MAP = {
#     "Nama Pembeli": "nama_pembeli",
#     "Nomor Telepon": "no_telepon",
#     "Alamat Lengkap": "alamat_lengkap",
#     "Kelurahan": "kelurahan",
#     "Kecamatan": "kecamatan",
#     "Kabupaten/Kota": "kabupaten_kota",
#     "Provinsi": "provinsi",
#     "Negara": "negara",
#     "Kode Pos": "kode_pos",
# }

# PRODUCTS_MAP = {
#     "SKU": "sku",
#     "Nama Produk": "nama_produk",
#     "Harga Awal Produk": "harga_awal_produk",
# }

# ORDERS_MAP = {
#     "Nomor Pesanan": "order_id",
#     "Status Pesanan": "order_status",
#     "Jenis Resi": "jenis_pesanan",
#     "Waktu Pesanan Dibuat": "waktu_pesanan_dibuat",
#     "Waktu Pesanan Dibayar": "waktu_pesanan_dibayar",
#     "Waktu Kedaluwarsa": "waktu_kadaluwarsa",
#     "Waktu Proses": "waktu_proses",
#     "Waktu Selesai": "waktu_selesai",
#     "Waktu Pembatalan": "waktu_pembatalan",
#     "Yang Membatalkan": "yang_membatalkan",
# }

# ORDER_ITEMS_MAP = {
#     "Nomor Pesanan": "order_id",
#     "Jumlah": "jumlah",
#     "Harga Satuan": "harga_satuan",
#     "Subtotal Produk": "subtotal_produk",
#     "Diskon Penjual": "diskon_penjual",
#     "Voucher": "voucher",
#     "Voucher Toko": "voucher_toko",
# }

# SHIPMENTS_MAP = {
#     "Nomor Pesanan": "order_id",
#     "Nomor Resi": "no_resi",
#     "Gudang Asal": "gudang_asal",
#     "Sesi Pengiriman": "sesi",
#     "Ongkos Kirim": "ongkos_kirim",
#     "Diskon Ongkos Kirim Penjual": "diskon_ongkos_kirim_penjual",
#     "Diskon Ongkos Kirim Marketplace": "diskon_ongkos_kirim_marketplace",
#     "Waktu Cetak": "waktu_cetak",
#     "Waktu Pesanan Dikirim": "waktu_pesanan_dikirim",
# }

# PAYMENTS_MAP = {
#     "Nomor Pesanan": "order_id",
#     "Total Pesanan": "total_pesanan",
#     "Biaya Pengelolaan": "biaya_pengelolaan",
#     "Biaya Transaksi": "biaya_transaksi",
# }
