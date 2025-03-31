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

# Configurações da NamSor API
NAMSOR_BASE_URL = 'https://v2.namsor.com/NamSorAPIv2/api2/json/gender'
#NAMSOR_API_KEY = '848cb906931f9c63c9532a912e8dfda9'  # Obtenha em https://www.namsor.com/
#NAMSOR_API_KEY = 'a2f3089a0dff7c55c36cf4fc23e822b0'
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
    """Salva o cache em disco"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(GENDER_CACHE, f, ensure_ascii=False, indent=2)

def get_gender(first_name: str, api_key: str) -> Dict:
    """
    Consulta a NamSor API para um único primeiro nome.
    Retorna um dicionário com {gender, probability}
    """
    # Verifica se o nome já está no cache
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
        response.raise_for_status()
        data = response.json()
        
        result = {
            'gender': data.get('likelyGender', 'unknown').lower(),
            'probability': data.get('probabilityCalibrated', 0)
        }

        # Adiciona ao cache
        GENDER_CACHE[first_name.lower()] = result
        return result

    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar NamSor API para {first_name}: {e}")
        return {'gender': 'unknown', 'probability': 0}

def extract_first_name(full_name: str) -> str:
    """
    Extrai o primeiro nome de forma robusta, tratando nomes compostos.
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

def process_author(author_str: str, api_key: str) -> Dict:
    """
    Processa um único autor.
    """
    full_name = author_str.strip()
    if not full_name:
        return None
        
    first_name = extract_first_name(full_name)
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
            time.sleep(REQUEST_DELAY)  # Respeita os limites da API
    
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

    with open(input_file, mode='r', encoding='utf-8') as infile, \
         open(output_file, mode='w', encoding='utf-8', newline='') as outfile, \
         open(authors_file, mode='w', encoding='utf-8', newline='') as authors_outfile:
        
        reader = csv.DictReader(infile)
        
        # Configura escritores CSV
        writer = csv.DictWriter(outfile, fieldnames=[
            'Title', 'Year', 'Male Authors', 'Female Authors', 
            'Unknown Gender Authors', 'First Author Female', 
            'Last Author Female', 'Total Authors'
        ])
        writer.writeheader()
        
        authors_writer = csv.DictWriter(authors_outfile, fieldnames=[
            'Article Title', 'Author Name', 'First Name',
            'Gender', 'Probability', 'Reliable'
        ])
        authors_writer.writeheader()
        
        for row in reader:
            title = row.get('Title', '')
            year = row.get('Publication Year', '')
            authors_str = row.get('Author', '').strip()
            
            # Skip articles with no authors
            if not authors_str:
                print(f"Pulando artigo sem autores: {title[:50]}...")
                continue
            
            print(f"Processando: {title[:50]}...")
            
            authors = process_all_authors(authors_str, api_key)
            stats = analyze_authors(authors)

            # Atualiza estatísticas anuais
            yearly_stats[year]['male_count'] += stats['male_count']
            yearly_stats[year]['female_count'] += stats['female_count']
            yearly_stats[year]['unknown_count'] += stats['unknown_count']
            yearly_stats[year]['total_authors'] += stats['total_authors']
            yearly_stats[year]['total_articles'] += 1
            
            if stats['has_female']:
                yearly_stats[year]['articles_with_female'] += 1
            if stats['first_author_female']:
                yearly_stats[year]['articles_first_female'] += 1
            if stats['last_author_female']:
                yearly_stats[year]['articles_last_female'] += 1
            
            # Atualiza estatísticas totais
            total_stats['male_count'] += stats['male_count']
            total_stats['female_count'] += stats['female_count']
            total_stats['unknown_count'] += stats['unknown_count']
            total_stats['total_authors'] += stats['total_authors']
            total_stats['total_articles'] += 1
            
            if stats['has_female']:
                total_stats['articles_with_female'] += 1
            if stats['first_author_female']:
                total_stats['articles_first_female'] += 1
            if stats['last_author_female']:
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
    
    # Gera o relatório anual
    generate_report(yearly_stats, total_stats)

if __name__ == '__main__':
    args = parse_arguments()
    NAMSOR_API_KEY = args.key
    INPUT_CSV = args.input

    print("Iniciando análise de gênero com NamSor API...")
    
    start_time = time.time()
    try:
        process_csv(INPUT_CSV, OUTPUT_CSV, AUTHORS_CSV, NAMSOR_API_KEY)
    finally:
        # Garante que o cache seja salvo mesmo se ocorrer um erro
        save_cache()
    elapsed_time = time.time() - start_time
    
    print(f"\nAnálise concluída em {elapsed_time:.2f} segundos.")