import csv
import json
from urllib.request import urlopen
import unidecode

# Configuração da Gender API
API_KEY = "91ccfe5f72e740efd29e639ee851afd1ea16a76b502d9a8a3a906fa3d08cf568"  # Substitua pela sua chave de API da Gender API

def parse_valid_name(name):
    # Remove acentos e espaços desnecessários
    name = unidecode.unidecode(name.strip())
    # Pega apenas o primeiro nome (antes do primeiro espaço)
    return name.split(' ')[0]

def get_gender(first_name):
    try:
        # Formata a URL da Gender API
        url = f"https://gender-api.com/get?key={API_KEY}&name={first_name}"
        
        # Faz a requisição à API
        response = urlopen(url)
        decoded = response.read().decode('utf-8')
        data = json.loads(decoded)
        
        # Depuração: Mostra a resposta completa da API
        print(f"Resposta da API para {first_name}: {data}")
        
        # Retorna o gênero determinado
        return data.get("gender", "undefined")
    except Exception as e:
        print(f"Erro ao acessar a API para o nome {first_name}: {e}")
        return "undefined"

def main():
    with open('womenLib.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile)
        with open('output.csv', 'w', newline='', encoding='utf-8') as outputfile:
            fieldnames = ['Title', 'Women Count', 'Men Count', 'Undefined Count', 'First Author is Woman', 'Last Author is Woman']
            writer = csv.DictWriter(outputfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in spamreader:
                # Verifica se a linha tem pelo menos 4 colunas
                if len(row) < 4:
                    print(f"Linha ignorada (formato inválido): {row}")
                    continue

                authors = row[3].split(';')
                women_count = 0
                men_count = 0
                undefined_count = 0
                first_author_gender = 'undefined'
                last_author_gender = 'undefined'

                for i, author in enumerate(authors):
                    if ',' in author:
                        # Extrai o primeiro nome (após a vírgula)
                        first_name = author.split(', ')[1].split(' ')[0]
                        gender = get_gender(first_name)
                        print(f"{first_name}: {gender}")
                        if gender == 'female':
                            women_count += 1
                        elif gender == 'male':
                            men_count += 1
                        else:
                            undefined_count += 1

                        if i == 0:
                            first_author_gender = gender
                        if i == len(authors) - 1:
                            last_author_gender = gender

                print(f"Artigo: {row[4]}")
                print(f"Autores: {authors}")
                print(f"Mulheres: {women_count}, Homens: {men_count}, Indefinidos: {undefined_count}")
                print(f"Primeiro autor é mulher? {first_author_gender == 'female'}")
                print(f"Último autor é mulher? {last_author_gender == 'female'}")
                print("-" * 50)

                writer.writerow({
                    'Title': row[4],
                    'Women Count': women_count,
                    'Men Count': men_count,
                    'Undefined Count': undefined_count,
                    'First Author is Woman': first_author_gender == 'female',
                    'Last Author is Woman': last_author_gender == 'female'
                })

if __name__ == "__main__":
    main()