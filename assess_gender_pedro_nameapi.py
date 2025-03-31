import csv
import os
import requests
from typing import List, Dict, Tuple
from functools import lru_cache

# Configurações
INPUT_CSV = 'womenLib_test.csv'
OUTPUT_DIR = 'assessed'
OUTPUT_CSV = os.path.join(OUTPUT_DIR, 'womenLibAssessed.csv')
AUTHORS_CSV = os.path.join(OUTPUT_DIR, 'womenLibAuthors.csv')

# Configurações da NameAPI
NAMEAPI_BASE_URL = 'https://api.nameapi.org/rest/v5.3/genderizer/persongenderizer'
NAMEAPI_API_KEY = '7a0dcac1b1927cce2ca86385071963db-user1'  # Obtenha em https://www.nameapi.org/
CONFIDENCE_THRESHOLD = 0.75  # 75% de confiança mínima

# Criar diretório de saída se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

@lru_cache(maxsize=1000)  # Cache para evitar chamadas repetidas à API
def get_gender_with_nameapi(first_name: str) -> Tuple[str, float]:
    """
    Consulta a NameAPI para determinar o gênero de um primeiro nome.
    Aplica filtro de confiança (75% como padrão).
    
    Args:
        first_name (str): Primeiro nome do autor
        
    Returns:
        Tuple[str, float]: (gênero, probabilidade)
        Gênero será 'male', 'female' ou 'unknown' (se confiança < threshold)
    """
    headers = {
        'Content-Type': 'application/json',
        'Api-Key': NAMEAPI_API_KEY
    }
    
    payload = {
        "inputPerson": {
            "type": "NaturalInputPerson",
            "personName": {
                "nameFields": [
                    {
                        "string": first_name,
                        "fieldType": "FIRSTNAME"
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.post(NAMEAPI_BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'gender' in data and 'confidence' in data:
            confidence = data['confidence'] / 100  # Convertendo para 0-1
            if confidence >= CONFIDENCE_THRESHOLD:
                gender = data['gender'].lower()  # Converte para lowercase
                return gender, confidence
            return 'unknown', confidence
        
        return 'unknown', 0.0
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar NameAPI para {first_name}: {e}")
        return 'unknown', 0.0

def extract_first_name(full_name: str) -> str:
    """
    Extrai o primeiro nome de um nome completo de forma robusta.
    """
    # Remove partes entre parênteses e espaços extras
    name = full_name.split('(')[0].strip()
    
    # Caso 1: Nome no formato "Sobrenome, Nome"
    if ',' in name:
        parts = [p.strip() for p in name.split(',')]
        if len(parts) > 1:
            return parts[1].split()[0]  # Pega o primeiro nome após a vírgula
    
    # Caso 2: Nome no formato "Nome Sobrenome"
    return name.split()[0]  # Pega a primeira parte

def process_authors(author_str: str) -> List[Dict]:
    """
    Processa a string de autores e retorna lista com informações de gênero.
    """
    if not author_str:
        return []
    
    authors = []
    for author in author_str.split(';'):
        author = author.strip()
        if not author:
            continue
            
        first_name = extract_first_name(author)
        gender, confidence = get_gender_with_nameapi(first_name)
        
        authors.append({
            'full_name': author,
            'first_name': first_name,
            'gender': gender,
            'probability': confidence,
            'reliable': confidence >= CONFIDENCE_THRESHOLD
        })
    
    return authors

def analyze_authors(authors: List[Dict]) -> Dict:
    """
    Analisa a lista de autores contando gêneros confiáveis e verificando posições.
    Considera apenas gêneros com confiança acima do threshold.
    """
    stats = {
        'male_count': 0,
        'female_count': 0,
        'unknown_count': 0,
        'first_author_female': False,
        'last_author_female': False,
        'total_authors': len(authors)
    }
    
    if not authors:
        return stats
    
    # Processa cada autor
    for i, author in enumerate(authors):
        gender = author['gender'] if author['reliable'] else 'unknown'
        
        if gender == 'male':
            stats['male_count'] += 1
        elif gender == 'female':
            stats['female_count'] += 1
            # Verifica se é primeiro ou último autor
            if i == 0:
                stats['first_author_female'] = True
            if i == len(authors) - 1:
                stats['last_author_female'] = True
        else:
            stats['unknown_count'] += 1
    
    return stats

def process_csv(input_file: str, output_file: str, authors_file: str):
    """
    Processa o arquivo CSV de entrada e gera os arquivos de saída.
    """
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
            authors_str = row.get('Author', '')
            
            authors = process_authors(authors_str)
            stats = analyze_authors(authors)
            
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

if __name__ == '__main__':
    print("Iniciando análise de gênero com NameAPI...")
    
    process_csv(INPUT_CSV, OUTPUT_CSV, AUTHORS_CSV)
    
    print(f"Análise concluída.")