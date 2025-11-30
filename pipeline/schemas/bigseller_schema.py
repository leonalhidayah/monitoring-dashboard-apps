import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

try:
    bigseller_schema = DataFrameSchema(
        {
            "Nomor Pesanan": Column(str, nullable=False),
            "Status Pesanan": Column(str, nullable=True),
            "Marketplace": Column(str, nullable=True),
            "Toko Marketplace": Column(str, nullable=True),
            "Nama Pembeli": Column(str, nullable=True),
            "Nomor Telepon": Column(str, nullable=True),
            "Kode Pos": Column(str, nullable=True),
            "Negara": Column(str, nullable=True),
            "Provinsi": Column(str, nullable=True),
            "Kabupaten/Kota": Column(str, nullable=True),
            "Kecamatan": Column(str, nullable=True),
            "Kelurahan": Column(str, nullable=True),
            "Alamat Lengkap": Column(str, nullable=True),
            "SKU": Column(str, nullable=False),
            "Nama Produk": Column(str, nullable=True),
            "Jumlah": Column(int, nullable=False, checks=Check.ge(0)),
            "Harga Satuan": Column(float, nullable=True, checks=Check.ge(0)),
            "Subtotal Produk": Column(float, nullable=True, checks=Check.ge(0)),
            "Harga Awal Produk": Column(float, nullable=True, checks=Check.ge(0)),
            "Jasa Kirim yang Dipilih Pembeli": Column(str, nullable=True),
            "Nomor Resi": Column(str, nullable=True),
            "Ongkos Kirim": Column(float, nullable=True, checks=Check.ge(0)),
            "Diskon Ongkos Kirim Penjual": Column(
                float, nullable=True, checks=Check.ge(0)
            ),
            "Diskon Ongkos Kirim Marketplace": Column(
                float, nullable=True, checks=Check.ge(0)
            ),
            "Total Pesanan": Column(float, nullable=False, checks=Check.ge(0)),
            "Metode Pembayaran": Column(str, nullable=True),
            "Biaya Pengelolaan": Column(float, nullable=True, checks=Check.ge(0)),
            "Biaya Transaksi": Column(float, nullable=True, checks=Check.ge(0)),
            "Diskon Penjual": Column(float, nullable=True, checks=Check.ge(0)),
            "Diskon Marketplace": Column(float, nullable=True, checks=Check.ge(0)),
            "Voucher": Column(float, nullable=True, checks=Check.ge(0)),
            "Voucher Toko": Column(float, nullable=True, checks=Check.ge(0)),
            "Waktu Pesanan Dibuat": Column(pa.DateTime, nullable=True),
            "Waktu Pesanan Dibayar": Column(pa.DateTime, nullable=True),
            "Waktu Kedaluwarsa": Column(pa.DateTime, nullable=True),
            "Waktu Proses": Column(pa.DateTime, nullable=True),
            "Waktu Cetak": Column(pa.DateTime, nullable=True),
            "Waktu Pesanan Dikirim": Column(pa.DateTime, nullable=True),
            "Waktu Selesai": Column(pa.DateTime, nullable=True),
            "Waktu Pembatalan": Column(pa.DateTime, nullable=True),
            "Gudang": Column(str, nullable=True),
            "Sesi Pengiriman": Column(str, nullable=True),
            "Jenis Resi": Column(str, nullable=True),
            "Tanggal Gudang": Column(pa.DateTime, nullable=True),
        },
        strict="filter",  # "filter" akan menghapus kolom yg tidak ada di skema
        coerce=True,  # Tetap paksa tipe data
    )
except pa.errors.SchemaInitError as e:
    print(f"Error initializing schema: {e}")
    raise
