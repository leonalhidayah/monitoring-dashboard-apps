import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

# Skema dimmension tables
dim_brands_schema = DataFrameSchema(
    {
        "nama_brand": Column(str, nullable=False, unique=True),
    },
    strict="filter",
    coerce=True,
)

dim_marketplaces_schema = DataFrameSchema(
    {
        "nama_marketplace": Column(str, nullable=False, unique=True),
    },
    strict="filter",
    coerce=True,
)

dim_shipping_services_schema = DataFrameSchema(
    {
        "jasa_kirim": Column(str, nullable=False, unique=True),
    },
    strict="filter",
    coerce=True,
)

dim_payment_methods_schema = DataFrameSchema(
    {
        "metode_pembayaran": Column(str, nullable=False, unique=True),
    },
    strict="filter",
    coerce=True,
)

dim_stores_schema = DataFrameSchema(
    {
        "nama_toko": Column(str, nullable=False, unique=True),
        "marketplace_id": Column(int, nullable=False, unique=False),
    },
    strict="filter",
    coerce=True,
)


# Skema untuk tabel 'orders' (data unik per pesanan)
orders_schema = DataFrameSchema(
    {
        "order_id": Column(str, nullable=False, unique=True),
        "customer_id": Column(int, nullable=True),
        "order_status": Column(str, nullable=True),
        "jenis_pesanan": Column(str, nullable=True),
        "waktu_pesanan_dibuat": Column(pa.DateTime, nullable=True),
        "waktu_pesanan_dibayar": Column(pa.DateTime, nullable=True),
        "waktu_kadaluwarsa": Column(pa.DateTime, nullable=True),
        "waktu_proses": Column(pa.DateTime, nullable=True),
        "waktu_selesai": Column(pa.DateTime, nullable=True),
        "waktu_pembatalan": Column(pa.DateTime, nullable=True),
        "timestamp_input_data": Column(pa.DateTime, nullable=True),
    },
    strict="filter",
    coerce=True,
)


# Skema untuk tabel 'order_items' (data per produk dalam pesanan)
order_items_schema = DataFrameSchema(
    {
        "order_id": Column(str, nullable=False),
        "product_id": Column(int, nullable=False),
        "store_id": Column(int, nullable=False),
        "jumlah": Column(int, nullable=False, checks=Check.gt(0)),
        "harga_satuan": Column(float, nullable=True, checks=Check.ge(0)),
        "subtotal_produk": Column(float, nullable=True, checks=Check.ge(0)),
        "diskon_penjual": Column(float, nullable=True, checks=Check.ge(0)),
        "voucher": Column(float, nullable=True, checks=Check.ge(0)),
        "voucher_toko": Column(float, nullable=True, checks=Check.ge(0)),
    },
    strict="filter",
    coerce=True,
)


shipments_schema = DataFrameSchema(
    {
        "order_id": Column(str, nullable=False),
        "no_resi": Column(str, nullable=False, unique=True),
        "service_id": Column(int, nullable=True),
        "gudang_asal": Column(str, nullable=True),
        "sesi": Column(str, nullable=True),
        "ongkos_kirim": Column(float, nullable=True, checks=Check.ge(0)),
        "diskon_ongkos_kirim_penjual": Column(float, nullable=True, checks=Check.ge(0)),
        "diskon_ongkos_kirim_marketplace": Column(
            float, nullable=True, checks=Check.ge(0)
        ),
        "waktu_cetak": Column(pa.DateTime, nullable=True),
        "waktu_pesanan_dikirim": Column(pa.DateTime, nullable=True),
    },
    strict="filter",
    coerce=True,
)


payments_schema = DataFrameSchema(
    {
        "order_id": Column(str, nullable=False),
        "method_id": Column(int, nullable=True),
        "total_pesanan": Column(float, nullable=True, checks=Check.ge(0)),
        "biaya_pengelolaan": Column(float, nullable=True, checks=Check.ge(0)),
        "biaya_transaksi": Column(float, nullable=True, checks=Check.ge(0)),
    },
    strict="filter",
    coerce=True,
)


dim_customers_schema = DataFrameSchema(
    {
        "nama_pembeli": Column(str, nullable=True),
        "no_telepon": Column(str, nullable=True),
        "alamat_lengkap": Column(str, nullable=True),
        "kelurahan": Column(str, nullable=True),
        "kecamatan": Column(str, nullable=True),
        "kabupaten_kota": Column(str, nullable=True),
        "provinsi": Column(str, nullable=True),
        "negara": Column(str, nullable=True),
        "kode_pos": Column(str, nullable=True),
    },
    strict="filter",
    coerce=True,
)

dim_products_schema = DataFrameSchema(
    {
        "sku": Column(str, nullable=False, unique=True),
        "nama_produk": Column(str, nullable=True),
        "brand_id": Column(int, nullable=False),
        "harga_awal_produk": Column(float, nullable=False, checks=Check.ge(0)),
    },
    strict="filter",
    coerce=True,
)
