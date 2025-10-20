import csv

def append_gold_hosts(ntnx_file, merged_file):
    # Detecta delimitador automaticamente para o ntnxCap.csv
    with open(ntnx_file, 'r', encoding='utf-8', newline='') as f:
        sample = f.read(2048)
        f.seek(0)
        dialect_ntnx = csv.Sniffer().sniff(sample, delimiters=";,")
        reader_ntnx = csv.DictReader(f, dialect_ntnx)
        gold_hosts = [
            row for row in reader_ntnx
            if "gold" in row.get("MachineName", "").lower()
        ]

    if not gold_hosts:
        print("[-] Nenhum host contendo 'GOLD' encontrado.")
        return

    print(f"[+] Encontrados {len(gold_hosts)} hosts contendo 'GOLD'.")

    # Detecta delimitador automaticamente no merged existente
    try:
        with open(merged_file, 'r', encoding='utf-8', newline='') as f:
            sample = f.read(2048)
            f.seek(0)
            dialect_merged = csv.Sniffer().sniff(sample, delimiters=";,")
            reader_merged = list(csv.DictReader(f, dialect_merged))
            existing_fields = [c.strip() for c in reader_merged[0].keys()] if reader_merged else []
    except FileNotFoundError:
        existing_fields = []

    # Função pra encontrar colunas com nomes semelhantes
    def find_col(possible_names):
        for name in existing_fields:
            for possible in possible_names:
                if name.lower().replace(" ", "") == possible.lower().replace(" ", ""):
                    return name
        return None

    # Mapeia as colunas reais (ou define padrão)
    col_host = find_col(["Host name", "Hostname", "Host"]) or "Host name"
    col_ip = find_col(["Host IP", "IP", "Address"]) or "Host IP"
    col_env = find_col(["Environment", "Env", "Ambiente"]) or "Environment"

    # Garante que os headers existem
    if not existing_fields:
        existing_fields = [col_host, col_ip, col_env]

    # Abre merged para append
    with open(merged_file, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=existing_fields, delimiter=';')
        # Escreve cabeçalho se o arquivo estava vazio
        if f.tell() == 0:
            writer.writeheader()

        for row in gold_hosts:
            writer.writerow({
                col_host: row.get("MachineName", "").strip(),
                col_ip: row.get("IPs", "").strip(),
                col_env: row.get("env", "").strip()
            })

    print(f"[+] {len(gold_hosts)} linhas adicionadas à planilha '{merged_file}'.")
