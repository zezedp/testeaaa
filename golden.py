import csv

def append_gold_hosts(ntnx_file, merged_file):
    # Detecta delimitador automaticamente
    with open(ntnx_file, 'r', encoding='utf-8', newline='') as f:
        sample = f.read(2048)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=";,")
        reader = csv.DictReader(f, dialect=dialect)

        gold_hosts = [
            row for row in reader
            if "gold" in row.get("MachineName", "").lower()
        ]

    if not gold_hosts:
        print("[-] Nenhum host contendo 'GOLD' encontrado.")
        return

    print(f"[+] Encontrados {len(gold_hosts)} hosts contendo 'GOLD'.")

    # Lê a planilha merged existente
    with open(merged_file, 'r', encoding='utf-8', newline='') as f:
        sample = f.read(2048)
        f.seek(0)
        dialect_merged = csv.Sniffer().sniff(sample, delimiters=";,")
        reader_merged = list(csv.DictReader(f, dialect=dialect_merged))
        fieldnames = reader_merged[0].keys() if reader_merged else [
            "Host name", "Host IP", "Environment"
        ]

    # Abre merged para append
    with open(merged_file, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        # Se o arquivo estava vazio, escreve header
        if f.tell() == 0:
            writer.writeheader()

        for row in gold_hosts:
            writer.writerow({
                "Host name": row.get("MachineName", "").strip(),
                "Host IP": row.get("IPs", "").strip(),
                "Environment": row.get("env", "").strip()
            })

    print(f"[+] {len(gold_hosts)} linhas adicionadas à planilha '{merged_file}'.")


# === Uso ===
append_gold_hosts("ntnxCap.csv", "merged_data_departamentos.csv")
