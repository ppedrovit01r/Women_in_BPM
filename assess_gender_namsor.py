import csv
import os
import requests
import time
import json
import sys
import argparse
from typing import List, Dict, DefaultDict
from collections import defaultdict

# Configurações
DEFAULT_INPUT_CSV = 'womenLib.csv'
OUTPUT_DIR = 'assessed'
timestamp = time.strftime("%Y%m%d_%H%M")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, f'LibAssessed_{timestamp}.csv')
AUTHORS_CSV = os.path.join(OUTPUT_DIR, f'Authors_{timestamp}.csv')
REPORT_CSV = os.path.join(OUTPUT_DIR, f'Report_{timestamp}.csv')
CACHE_FILE = os.path.join(OUTPUT_DIR, 'gender_cache.json')
STATE_FILE = os.path.join(OUTPUT_DIR, 'processing_state.json')
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "progress.log")
QUOTA_EXCEEDED_MESSAGE = "API quota exceeded"  # Message to look for in API responses

# Configurações da NamSor API
NAMSOR_BASE_URL = 'https://v2.namsor.com/NamSorAPIv2/api2/json/gender'
#NAMSOR_API_KEY =  # Obtenha em https://www.namsor.com/
CONFIDENCE_THRESHOLD = 0.75  # 75% de confiança mínima
REQUEST_DELAY = 1  # Delay entre chamadas em segundos

def parse_arguments():
    """
    Analisa os argumentos da linha de comando.
    """
    parser = argparse.ArgumentParser(description='Analisa gênero de autores usando a API NamSor')
    parser.add_argument('-i', '--input', type=str, default=DEFAULT_INPUT_CSV,
                       help=f'Nome do arquivo CSV de entrada (padrão: {DEFAULT_INPUT_CSV})')
    parser.add_argument('-k', '--key', type=str, required=True,
                       help='Chave da API NamSor (obrigatório)')
    return parser.parse_args()

# Criar diretório de saída se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Carregar cache existente ou criar novo
try:
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        GENDER_CACHE = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    GENDER_CACHE = {}

def save_cache():
    """Salva a cache imediatamente."""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(GENDER_CACHE, f, ensure_ascii=False, indent=2)

def load_cache():
    """Carrega a cache de gênero existente, se disponível."""
    global GENDER_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                GENDER_CACHE = json.load(f)
                print(f"✅ Cache carregada com {len(GENDER_CACHE)} registros.")
        except (json.JSONDecodeError, IOError):
            print("⚠️ Erro ao carregar a cache, iniciando nova cache.")
            GENDER_CACHE = {}
    else:
        print("⚠️ Nenhuma cache encontrada, criando nova.")
        GENDER_CACHE = {}


def get_gender(first_name: str, api_key: str) -> Dict:
    """Consulta a NamSor API ou usa cache"""
    cached_result = GENDER_CACHE.get(first_name.lower())
    if cached_result:
        return cached_result

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-API-KEY': api_key
    }

    try:
        response = requests.get(f"{NAMSOR_BASE_URL}/{first_name}", headers=headers)
        if response.status_code == 401:
            print("\n" + "="*50)
            print(f"ERRO CRÍTICO: Chave API inválida ou não autorizada (401 Unauthorized)")
            print("A API Key fornecida não tem permissão ou está errada.")
            print("Verifique sua chave e tente novamente.")
            print("="*50)
            sys.exit(1)  # Sai imediatamente para evitar chamadas desnecessárias

        if response.status_code == 403:
            print("\n" + "="*50)
            print(f"ERRO CRÍTICO: Chave API bloqueada ou cota excedida (403 Forbidden)")
            print("Troque a chave API e reinicie o script.")
            print("="*50)
            sys.exit(1)

        response.raise_for_status()
        data = response.json()

        result = {
            'gender': data.get('likelyGender', 'unknown').lower(),
            'probability': data.get('probabilityCalibrated', 0)
        }

        GENDER_CACHE[first_name.lower()] = result
        save_cache()  # Salva imediatamente para evitar perda de dados
        return result

    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar NamSor API para {first_name}: {e}")
        return {'gender': 'unknown', 'probability': 0}


def get_last_processed_line(input_file):
    """Lê a última linha processada do log, garantindo que o mesmo CSV está sendo usado."""
    try:
        with open(PROGRESS_FILE, "r") as f:
            saved_csv, last_line = f.read().strip().split(',')
            if saved_csv == input_file:  # Verifica se o CSV é o mesmo
                return int(last_line)
    except (FileNotFoundError, ValueError):
        pass
    return 0  # Retorna 0 se o log estiver ausente ou o CSV for diferente


def save_progress(input_file, line_number):
    """Salva o nome do CSV e a última linha processada no log."""
    with open(PROGRESS_FILE, "w") as f:
        f.write(f"{input_file},{line_number}")


def extract_first_name(full_name: str) -> str:
    """
    Extrai o primeiro nome de forma robusta, tratando nomes compostos.
    Retorna None para nomes com inicial única (ex: "W. Smith")
    """
    # Remove partes entre parênteses e espaços extras
    name = full_name.split('(')[0].strip()
    
    # Caso 1: Nome no formato "Sobrenome, Nome"
    if ',' in name:
        parts = [p.strip() for p in name.split(',')]
        if len(parts) > 1:
            first_part = parts[1].split()[0]  # Primeiro nome após a vírgula
            # Se for inicial única (ex: "W."), retorna None
            if len(first_part) == 2 and first_part.endswith('.'):
                return None
            # Se for nome composto com hífen, pega a primeira parte
            return first_part.split('-')[0]
    
    # Caso 2: Nome no formato "Nome Sobrenome"
    parts = name.split()
    if not parts:
        return None
    
    first_part = parts[0]  # Primeiro nome
    # Se for inicial única (ex: "W."), retorna None
    if len(first_part) == 2 and first_part.endswith('.'):
        return None
    # Se for nome composto com hífen, pega a primeira parte
    return first_part.split('-')[0]

def process_author(author_str: str, api_key: str) -> Dict:
    """
    Processa um único autor.
    """
    full_name = author_str.strip()
    if not full_name:
        return None
        
    first_name = extract_first_name(full_name)
    # Se for inicial única, retorna como "unknown" sem chamar a API
    if first_name is None:
        return {
            'full_name': full_name,
            'first_name': '',  # Indica que foi pulado
            'gender': 'unknown',
            'probability': 0,
            'reliable': False
        }
    
    # Verifica se o nome já está no cache
    cached_result = GENDER_CACHE.get(first_name.lower())
    if cached_result:
        return {
            'full_name': full_name,
            'first_name': first_name,
            'gender': cached_result['gender'],
            'probability': cached_result['probability'],
            'reliable': cached_result['probability'] >= CONFIDENCE_THRESHOLD
        }
    
    # Só aplica o delay se for chamar a API
    time.sleep(REQUEST_DELAY)
    gender_data = get_gender(first_name, api_key)
    
    probability = gender_data.get('probability', 0)
    gender = gender_data.get('gender', 'unknown')
    
    # Aplica o filtro de confiança
    if probability < CONFIDENCE_THRESHOLD:
        gender = 'unknown'
    
    return {
        'full_name': full_name,
        'first_name': first_name,
        'gender': gender,
        'probability': probability,
        'reliable': probability >= CONFIDENCE_THRESHOLD
    }

def process_all_authors(author_str: str, api_key: str) -> List[Dict]:
    """
    Processa todos os autores de uma string.
    """
    if not author_str:
        return []
    
    authors = []
    for full_name in author_str.split(';'):
        full_name = full_name.strip()
        if not full_name:
            continue
            
        author = process_author(full_name, api_key)
        if author:
            authors.append(author)
    
    return authors

def analyze_authors(authors: List[Dict]) -> Dict:
    """
    Analisa a lista de autores contando gêneros confiáveis e verificando posições.
    """
    stats = {
        'male_count': 0,
        'female_count': 0,
        'unknown_count': 0,
        'has_female': False,
        'first_author_female': False,
        'last_author_female': False,
        'total_authors': len(authors)
    }
    
    if not authors:
        return stats
    
    for i, author in enumerate(authors):
        gender = author['gender'] if author['reliable'] else 'unknown'
        
        if gender == 'male':
            stats['male_count'] += 1
        elif gender == 'female':
            stats['female_count'] += 1
            stats['has_female'] = True
            # Verifica se é primeiro ou último autor
            if i == 0:
                stats['first_author_female'] = True
            if i == len(authors) - 1:
                stats['last_author_female'] = True
        else:
            stats['unknown_count'] += 1
    
    return stats

def generate_report(yearly_stats: Dict, total_stats: Dict):
    """
    Gera o relatório anual com estatísticas agregadas.
    """
    with open(REPORT_CSV, mode='w', encoding='utf-8', newline='') as report_file:
        writer = csv.DictWriter(report_file, fieldnames=[
            'Year',
            'Male Authors', 
            'Percentage Male Authors', 
            'Female Authors', 
            'Percentage Female Authors',
            'Unknown Gender Authors', 
            'Percentage Unknown Gender Authors',
            'Articles with at least one woman', 
            'Percentage Articles with at least one woman',
            'Articles with female first author', 
            'Percentage Articles with female first author',
            'Articles with female last author', 
            'Percentage Articles with female last author',
            'Total Articles', 
            'Total Authors'
        ])
        writer.writeheader()
        
        # Escreve os dados por ano
        for year in sorted(yearly_stats.keys()):
            stats = yearly_stats[year]
            total_articles = stats['total_articles']
            total_authors = stats['total_authors']
            
            writer.writerow({
                'Year': year,
                'Male Authors': stats['male_count'],
                'Percentage Male Authors': round((stats['male_count'] / total_authors * 100) if total_authors > 0 else 0,2),
                'Female Authors': stats['female_count'],
                'Percentage Female Authors': round((stats['female_count'] / total_authors * 100) if total_authors > 0 else 0,2),
                'Unknown Gender Authors': stats['unknown_count'],
                'Percentage Unknown Gender Authors': round((stats['unknown_count'] / total_authors * 100) if total_authors > 0 else 0,2),
                'Articles with at least one woman': stats['articles_with_female'],
                'Percentage Articles with at least one woman': round((stats['articles_with_female'] / total_articles * 100) if total_articles > 0 else 0,2),
                'Articles with female first author': stats['articles_first_female'],
                'Percentage Articles with female first author': round((stats['articles_first_female'] / total_articles * 100) if total_articles > 0 else 0,2),
                'Articles with female last author': stats['articles_last_female'],
                'Percentage Articles with female last author': round((stats['articles_last_female'] / total_articles * 100) if total_articles > 0 else 0,2),
                'Total Articles': total_articles,
                'Total Authors': total_authors
            })
        
        # Escreve o total geral
        total_articles = total_stats['total_articles']
        total_authors = total_stats['total_authors']
        writer.writerow({
            'Year': 'TOTAL',
            'Male Authors': total_stats['male_count'],
            'Percentage Male Authors': round((total_stats['male_count'] / total_authors * 100) if total_authors > 0 else 0,2),
            'Female Authors': total_stats['female_count'],
            'Percentage Female Authors': round((total_stats['female_count'] / total_authors * 100) if total_authors > 0 else 0,2),
            'Unknown Gender Authors': total_stats['unknown_count'],
            'Percentage Unknown Gender Authors': round((total_stats['unknown_count'] / total_authors * 100) if total_authors > 0 else 0,2),
            'Articles with at least one woman': total_stats['articles_with_female'],
            'Percentage Articles with at least one woman': round((total_stats['articles_with_female'] / total_articles * 100) if total_articles > 0 else 0,2),
            'Articles with female first author': total_stats['articles_first_female'],
            'Percentage Articles with female first author': round((total_stats['articles_first_female'] / total_articles * 100) if total_articles > 0 else 0,2),
            'Articles with female last author': total_stats['articles_last_female'],
            'Percentage Articles with female last author': round((total_stats['articles_last_female'] / total_articles * 100) if total_articles > 0 else 0,2),
            'Total Articles': total_articles,
            'Total Authors': total_authors
        })

def process_csv(input_file: str, output_file: str, authors_file: str, api_key: str):
    """
    Processa o arquivo CSV de entrada e gera os arquivos de saída.
    Pode retomar de onde parou se a cota da API foi excedida.
    """

    yearly_stats = defaultdict(lambda: {
        'male_count': 0,
        'female_count': 0,
        'unknown_count': 0,
        'articles_with_female': 0,
        'articles_first_female': 0,
        'articles_last_female': 0,
        'total_articles': 0,
        'total_authors': 0
    })
    
    total_stats = {
        'male_count': 0,
        'female_count': 0,
        'unknown_count': 0,
        'articles_with_female': 0,
        'articles_first_female': 0,
        'articles_last_female': 0,
        'total_articles': 0,
        'total_authors': 0
    }

    last_line = get_last_processed_line(input_file)  # Obtém última linha processada

    with open(input_file, mode='r', encoding='utf-8') as infile, \
         open(output_file, mode='a' if last_line > 0 else 'w', encoding='utf-8', newline='') as outfile, \
         open(authors_file, mode='a' if last_line > 0 else 'w', encoding='utf-8', newline='') as authors_outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=[
            'Title', 'Year', 'Male Authors', 'Female Authors', 
            'Unknown Gender Authors', 'First Author Female', 
            'Last Author Female', 'Total Authors'
        ])
        authors_writer = csv.DictWriter(authors_outfile, fieldnames=[
            'Article Title', 'Author Name', 'First Name',
            'Gender', 'Probability', 'Reliable'
        ])

        # Escreve cabeçalhos apenas se for uma nova execução
        if last_line == 0:
            writer.writeheader()
            authors_writer.writeheader()

        for line_number, row in enumerate(reader, start=1):
            if line_number <= last_line:
                continue  # Pula linhas já processadas

            try:
                title = row.get('Title', '')
                year = row.get('Publication Year', '')
                authors_str = row.get('Author', '').strip()

                # Pula artigos sem autores
                if not authors_str:
                    print(f"Pulando artigo sem autores (linha {line_number}): {title[:50]}...")
                    continue

                print(f"Processando linha {line_number}: {title[:50]}...")

                authors = process_all_authors(authors_str, api_key)
                stats = analyze_authors(authors)

                # Atualiza estatísticas anuais e totais
                yearly_stats[year]['male_count'] += stats['male_count']
                yearly_stats[year]['female_count'] += stats['female_count']
                yearly_stats[year]['unknown_count'] += stats['unknown_count']
                yearly_stats[year]['total_authors'] += stats['total_authors']
                yearly_stats[year]['total_articles'] += 1

                total_stats['male_count'] += stats['male_count']
                total_stats['female_count'] += stats['female_count']
                total_stats['unknown_count'] += stats['unknown_count']
                total_stats['total_authors'] += stats['total_authors']
                total_stats['total_articles'] += 1

                if stats['has_female']:
                    yearly_stats[year]['articles_with_female'] += 1
                    total_stats['articles_with_female'] += 1
                if stats['first_author_female']:
                    yearly_stats[year]['articles_first_female'] += 1
                    total_stats['articles_first_female'] += 1
                if stats['last_author_female']:
                    yearly_stats[year]['articles_last_female'] += 1
                    total_stats['articles_last_female'] += 1

                # Escreve no arquivo principal
                writer.writerow({
                    'Title': title,
                    'Year': year,
                    'Male Authors': stats['male_count'],
                    'Female Authors': stats['female_count'],
                    'Unknown Gender Authors': stats['unknown_count'],
                    'First Author Female': stats['first_author_female'],
                    'Last Author Female': stats['last_author_female'],
                    'Total Authors': stats['total_authors']
                })

                # Escreve no arquivo de autores
                for author in authors:
                    authors_writer.writerow({
                        'Article Title': title,
                        'Author Name': author['full_name'],
                        'First Name': author['first_name'],
                        'Gender': author['gender'],
                        'Probability': author['probability'],
                        'Reliable': author['reliable']
                    })

                # Salva progresso no log
                save_progress(input_file, line_number)

            except requests.exceptions.RequestException as e:
                if "403" in str(e):
                    print("\nERRO CRÍTICO: Chave API inválida ou sem permissão (403 Forbidden).")
                    print("Troque a chave API e reinicie o script.")
                    sys.exit(1)
                elif "quota exceeded" in str(e).lower():
                    print("\nATENÇÃO: COTA DA API EXCEDIDA na linha", line_number)
                    print("Salvando estado atual para continuar depois...")
                    save_cache()
                    sys.exit(1)
                else:
                    print(f"\nErro inesperado na linha {line_number}: {e}")
                    sys.exit(1)

            except Exception as e:
                print(f"\nERRO INESPERADO na linha {line_number}: {e}")
                sys.exit(1)

    # Gera o relatório ao final
    generate_report(yearly_stats, total_stats)

if __name__ == '__main__':
    args = parse_arguments()
    NAMSOR_API_KEY = args.key if args.key != "None" else None
    INPUT_CSV = args.input

    print("Iniciando análise de gênero com NamSor API...")
    
    start_time = time.time()
    try:
        load_cache()
        process_csv(INPUT_CSV, OUTPUT_CSV, AUTHORS_CSV, NAMSOR_API_KEY)
    finally:
        # Garante que o cache seja salvo mesmo se ocorrer um erro
        save_cache()
    elapsed_time = time.time() - start_time
    
    print(f"\nAnálise concluída em {elapsed_time:.2f} segundos.")