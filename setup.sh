# setup.sh

#!/bin/bash

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Jalankan Tailscale di background
# Gunakan auth key dari secrets untuk login tanpa interaksi
sudo tailscale up --authkey=${TS_AUTH_KEY} --hostname=streamlit-app &

# Tunggu beberapa detik agar Tailscale stabil
sleep 5

# Jalankan aplikasi Streamlit (ini akan dijalankan oleh Streamlit Cloud secara otomatis setelah script ini selesai)