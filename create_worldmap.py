import pandas as pd
import plotly.express as px
import re
import argparse
import requests
from collections import defaultdict
from time import sleep

# --- Função para extrair país do campo 'Extra' ---
def extract_country(text):
    if not isinstance(text, str):
        return None
    normalized_text = re.sub(r'^(event-place:|Place:)\s*', '', text, flags=re.IGNORECASE)
    if "Publisher" in normalized_text:
        normalized_text = normalized_text.split("Publisher")[0].strip()
    parts = [p.strip() for p in normalized_text.split(",") if p.strip()]
    if not parts:
        return None
    country = parts[-1]
    country_mapping = {
        "USA": "United States",
        "US": "United States",
        "UK": "United Kingdom",
        "U.K.": "United Kingdom",
    }
    return country_mapping.get(country, country)

# --- Função para buscar país via DOI (Crossref API) ---
def get_country_from_doi(doi):
    if not isinstance(doi, str) or not doi.strip():
        return None
    url = f"https://api.crossref.org/works/{doi.strip()}"
    try:
        response = requests.get(url, timeout=10).json()
        authors = response["message"].get("author", [])
        for author in authors:
            if "affiliation" in author:
                for aff in author["affiliation"]:
                    if "country" in aff:
                        return aff["country"]
    except Exception as e:
        print(f"Erro ao buscar DOI {doi}: {e}")
    return None

# --- Lógica principal ---
def main(input_file):
    # Lê o CSV (tenta aba 'Extra', senão primeira aba)
    try:
        df = pd.read_csv(input_file, sheet_name="Extra")
    except:
        df = pd.read_csv(input_file)
    
    # Verifica colunas necessárias
    target_columns = [col for col in df.columns if "extra" in col.lower() or "event-place" in col.lower()]
    if not target_columns:
        print("ERRO: Nenhuma coluna 'Extra' ou 'event-place' encontrada!")
        return
    
    # Processa cada linha
    countries = []
    for _, row in df.iterrows():
        country = None
        
        # 1. Tenta extrair do campo 'Extra' ou similar
        for col in target_columns:
            country = extract_country(row[col])
            if country:
                break
        
        # 2. Se não encontrou, tenta usar o DOI (se existir no CSV)
        if not country and "DOI" in df.columns:
            country = get_country_from_doi(row["DOI"])
            sleep(1)  # Respeita rate limit da API (1 requisição/segundo)
        
        countries.append(country if country else None)
    
    # Contagem de frequências
    freq = defaultdict(int)
    for country in countries:
        if country:
            freq[country] += 1
    
    # Salva resultados
    freq_df = pd.DataFrame(list(freq.items()), columns=["country", "frequency"])
    freq_df.to_csv("place_frequency.csv", index=False)
    print("Arquivo 'place_frequency.csv' gerado com sucesso!")
    
    # Gera mapa (se houver dados)
    if not freq_df.empty:
        fig = px.scatter_geo(
            freq_df,
            locations="country",
            locationmode="country names",
            size="frequency",
            hover_name="country",
            projection="natural earth",
            title="Scatter World Map by Country Frequency"
        )
        fig.show()
    else:
        print("Nenhum país válido encontrado para gerar o mapa.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Arquivo CSV de entrada")
    args = parser.parse_args()
    main(args.input)