import csv
from collections import defaultdict

def extract_first_name(full_name: str) -> str:
    """
    Extrai o primeiro nome de forma robusta, tratando nomes compostos com hífen.
    (Same function as in your assess_gender.py)
    """
    # Remove partes entre parênteses e espaços extras
    name = full_name.split('(')[0].strip()
    
    # Caso 1: Nome no formato "Sobrenome, Nome"
    if ',' in name:
        parts = [p.strip() for p in name.split(',')]
        if len(parts) > 1:
            first_part = parts[1].split()[0]  # Primeiro nome após a vírgula
            # Se for nome composto com hífen, pega a primeira parte
            return first_part.split('-')[0]
    
    # Caso 2: Nome no formato "Nome Sobrenome"
    parts = name.split()
    first_part = parts[0]  # Primeiro nome
    # Se for nome composto com hífen, pega a primeira parte
    return first_part.split('-')[0]

def count_names(csv_file: str):
    """
    Analisa os autores no arquivo CSV
    """
    first_name_counts = defaultdict(int)
    total_names = 0
    
    with open(csv_file, mode='r', encoding='utf-8') as file:
        # Usa o Sniffer para detectar o delimitador
        dialect = csv.Sniffer().sniff(file.read(1024))
        file.seek(0)
        
        reader = csv.DictReader(file, dialect=dialect)
        
        for row in reader:
            authors_str = row.get('Author', '').strip()
            if not authors_str:
                continue
                
            for full_name in authors_str.split(';'):
                full_name = full_name.strip()
                if not full_name:
                    continue
                    
                first_name = extract_first_name(full_name)
                first_name_counts[first_name] += 1
                total_names += 1
    
    # Calcula repetições
    repetitions = {name: count for name, count in first_name_counts.items() if count > 1}
    total_repetitions = sum(repetitions.values()) - len(repetitions)  # Total de ocorrências além da primeira
    
    print(f"Total de nomes encontrados: {total_names}")
    print(f"Total de primeiros nomes únicos: {len(first_name_counts)}")
    print(f"Total de repetições de primeiro nome: {total_repetitions}")
    
    if total_names > 0:
        repetition_percentage = (total_repetitions / total_names) * 100
        print(f"Porcentagem de repetições: {repetition_percentage:.2f}%")
    
    #print("\nPrimeiros nomes que se repetem:")
    #for name, count in sorted(repetitions.items(), key=lambda x: x[1], reverse=True):
    #    print(f"{name}: {count} ocorrências")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Uso: python analyze_authors.py <arquivo_csv>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    count_names(csv_file)