import json

def load_knowledge_base():
    with open("kb_lele.json", "r", encoding="utf-8") as file:
        return json.load(file)

def forward_chaining(fakta_awal, aturan):
    memori = set(fakta_awal)
    aturan_dijalankan = []

    while True:
        aturan_aktif = None

        for rule in aturan:
            if rule["kesimpulan"] in memori:
                continue

            kondisi = rule["kondisi"]

            if rule["mode"] == "dan":
                terpenuhi = all(f in memori for f in kondisi)
                pemicu = kondisi if terpenuhi else []

            else:
                pemicu = [f for f in kondisi if f in memori]
                terpenuhi = len(pemicu) > 0

            if terpenuhi:
                aturan_aktif = rule.copy()
                aturan_aktif["pemicu"] = pemicu
                break

        if aturan_aktif is None:
            break

        memori.add(aturan_aktif["kesimpulan"])
        aturan_dijalankan.append(aturan_aktif)

    return memori, aturan_dijalankan

def tampilkan_alasan(fakta, fakta_awal, aturan_dijalankan,
                     level=1, sudah=None):
    if sudah is None:
        sudah = set()

    indentasi = "  " * level

    if fakta in sudah:
        print(f"{indentasi}{fakta.replace('_', ' ')} <- Sudah dijelaskan")
        return

    sudah.add(fakta)

    if fakta in fakta_awal:
        print(f"{indentasi}{fakta.replace('_', ' ')} <- Fakta awal")
        return

    for rule in aturan_dijalankan:
        if rule["kesimpulan"] == fakta:

            pemicu = ", ".join(rule["pemicu"])
            sumber = ", ".join(rule["sumber"])

            print(
                f"{indentasi}{fakta.replace('_', ' ')} "
                f"<- {rule['id']} ({pemicu}) (Sumber {sumber})"
            )

            for kondisi in rule["pemicu"]:
                tampilkan_alasan(
                    kondisi,
                    fakta_awal,
                    aturan_dijalankan,
                    level + 1,
                    sudah
                )
            return


def main():
    data = load_knowledge_base()
    aturan = data["aturan"]

    print("=" * 65)
    print(" SISTEM PAKAR IDENTIFIKASI KUALITAS AIR KOLAM LELE")
    print("                  METODE FORWARD CHAINING")
    print("=" * 65)

    try:
        ph = float(input("\nMasukkan nilai pH air (0-14): "))
        suhu = float(input("Masukkan suhu air (°C): "))
        do = float(input("Masukkan kadar oksigen terlarut / DO (mg/L): "))
        jawaban = input(
            "Apakah ikan sering muncul di permukaan? (y/n): "
        ).strip().lower()

        if not 0 <= ph <= 14:
            print("\nError: pH harus berada antara 0 sampai 14.")
            return

        if not -5 <= suhu <= 60:
            print("\nError: Suhu berada di luar batas input.")
            return

        if not 0 <= do <= 30:
            print("\nError: DO berada di luar batas input.")
            return

        if jawaban not in ["y", "n"]:
            print("\nError: Masukkan jawaban y atau n.")
            return

    except ValueError:
        print("\nError: Input harus berupa angka yang valid.")
        return

    ikan_di_permukaan = jawaban == "y"
    fakta_awal = []

    if do < 3:
        fakta_awal.append("do_rendah")

    if ph < 6.5 or ph > 8.8:
        fakta_awal.append("ph_di_luar_rentang")

    if suhu < 27 or suhu > 30:
        fakta_awal.append("suhu_di_luar_rentang")

    if ikan_di_permukaan:
        fakta_awal.append("ikan_di_permukaan")

    status_ph = "Normal" if 6.5 <= ph <= 8.8 else "Tidak ideal"
    status_suhu = "Normal" if 27 <= suhu <= 30 else "Tidak ideal"
    status_do = "Memenuhi ambang operasional" if do >= 3 else "Rendah"
    status_ikan = "Ya" if ikan_di_permukaan else "Tidak"

    print("\n" + "=" * 65)
    print("1. HASIL PEMERIKSAAN PARAMETER")
    print("=" * 65)

    print(f"pH air                : {ph} ({status_ph})")
    print(f"Suhu air              : {suhu} °C ({status_suhu})")
    print(f"Oksigen terlarut (DO) : {do} mg/L ({status_do})")
    print(f"Ikan di permukaan     : {status_ikan}")

    if not fakta_awal:
        print("\nKualitas air kolam lele berada dalam kondisi normal.")
        print("Tidak ditemukan indikasi penyimpangan.")
        return
    hasil, aturan_dijalankan = forward_chaining(fakta_awal, aturan)

    print("\n" + "=" * 65)
    print("2. FAKTA AWAL")
    print("=" * 65)

    for fakta in fakta_awal:
        print(f"- {fakta}")

    print("\n" + "=" * 65)
    print("3. PROSES INFERENSI FORWARD CHAINING")
    print("=" * 65)

    for i, rule in enumerate(aturan_dijalankan, start=1):
        print(f"Siklus {i}: {rule['id']} -> {rule['kesimpulan']}")

    kesimpulan = [
        rule["kesimpulan"] for rule in aturan_dijalankan
    ]

    print("\n" + "=" * 65)
    print("KESIMPULAN")
    print("=" * 65)

    if kesimpulan:
        daftar_kesimpulan = [
            fakta.replace("_", " ") for fakta in kesimpulan
        ]

        print(", ".join(daftar_kesimpulan).capitalize() + ".")
        print("\nAlasan:")

        sudah = set()

        for fakta in kesimpulan:
            tampilkan_alasan(
                fakta,
                fakta_awal,
                aturan_dijalankan,
                sudah=sudah
            )

    else:
        print("Belum terdapat kesimpulan berdasarkan aturan yang tersedia.")

    print("\nCatatan:")
    print(
        "Aturan dan ambang parameter disusun berdasarkan "
        "sumber referensi yang tercantum dalam basis pengetahuan."
    )
    print(
        "Hasil identifikasi merupakan indikasi awal dan bukan "
        "pengganti pengukuran kualitas air secara menyeluruh."
    )

    print("\nProses identifikasi selesai.")

if __name__ == "__main__":
    main()
