import json
import csv
import argparse
from pathlib import Path

def update_gender_cache(csv_path, json_path, output_path=None):
    """
    Atualiza o cache de gêneros a partir de um arquivo CSV, evitando duplicatas.
    
    Args:
        csv_path (str): Caminho para o arquivo CSV
        json_path (str): Caminho para o arquivo JSON existente
        output_path (str, optional): Caminho para salvar o JSON atualizado. Se None, sobrescreve o original.
    """
    # Carrega o cache existente
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        cache = {}
    
    # Contadores para estatísticas
    added = 0
    updated = 0
    skipped = 0
    
    # Lê o CSV e processa os dados
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            first_name = row['First Name'].lower().strip()
            gender = row['Gender'].lower().strip()
            
            try:
                probability = float(row['Probability'])
            except (ValueError, KeyError):
                skipped += 1
                continue
            
            # Verifica se o registro é válido
            if probability <= 0:
                skipped += 1
                continue
                
            # Verifica se é um novo registro ou precisa atualizar
            if first_name not in cache:
                cache[first_name] = {
                    'gender': gender,
                    'probability': probability
                }
                added += 1
            elif probability > cache[first_name]['probability']:
                cache[first_name] = {
                    'gender': gender,
                    'probability': probability
                }
                updated += 1
            else:
                skipped += 1
    
    # Salva o arquivo atualizado
    output_path = output_path or json_path
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    
    return added, updated, skipped

def main():
    parser = argparse.ArgumentParser(
        description='Atualiza cache de gêneros a partir de um arquivo CSV',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-i', '--input', required=True,
                       help='Arquivo CSV de entrada com os dados dos autores')
    parser.add_argument('-c', '--cache', required=True,
                       help='Arquivo JSON com o cache existente')
    parser.add_argument('-o', '--output',
                       help='Arquivo de saída (opcional, sobrescreve o cache se não informado)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Mostra informações detalhadas do processamento')
    
    args = parser.parse_args()
    
    # Verifica se os arquivos existem
    if not Path(args.input).exists():
        print(f"Erro: Arquivo CSV '{args.input}' não encontrado!")
        return 1
        
    if not Path(args.cache).exists():
        print(f"Aviso: Arquivo JSON '{args.cache}' não encontrado. Criando novo cache.")
    
    try:
        added, updated, skipped = update_gender_cache(
            args.input,
            args.cache,
            args.output
        )
        
        if args.verbose:
            print("\nEstatísticas de processamento:")
            print(f"- Nomes adicionados: {added}")
            print(f"- Nomes atualizados: {updated}")
            print(f"- Registros ignorados: {skipped}")
            print(f"\nCache salvo em: {args.output or args.cache}")
        else:
            print(f"Cache atualizado com sucesso! Total de atualizações: {added + updated}")
            
        return 0
        
    except Exception as e:
        print(f"Erro durante o processamento: {str(e)}")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())