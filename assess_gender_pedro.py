import csv
import json
import requests
import unidecode

def parse_valid_name(name):
    # Remove acentos e espaços desnecessários
    name = unidecode.unidecode(name.strip())
    # Pega apenas o primeiro nome (antes do primeiro espaço)
    return name.split(' ')[0]

def get_gender(first_name):
    try:
        # URL da API com o nome formatado
        url = 'https://api.genderize.io?name=' + parse_valid_name(first_name) + '&apikey=4661e8f7692ad7106c16dbb9dc397948'
        print(f"Enviando requisição para: {url}")  # Depuração: Mostra a URL da requisição

        genderize_response = requests.get(url)
        print(f"Resposta da API: {genderize_response.text}")  # Depuração: Mostra a resposta da API

        parsed_gender = json.loads(genderize_response.content)
        
        # Verifica se a resposta contém as chaves esperadas
        if 'probability' in parsed_gender and 'count' in parsed_gender:
            if parsed_gender['probability'] >= 0.75 and parsed_gender['count'] >= 2:
                return parsed_gender['gender']
            else:
                return 'undefined'
        else:
            # Se a resposta não contém as chaves esperadas, retorna 'undefined'
            return 'undefined'
    except Exception as e:
        print(f"Erro ao acessar a API para o nome {first_name}: {e}")
        return 'undefined'

def main():
    with open('womenLib.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile)
        with open('output.csv', 'w', newline='', encoding='utf-8') as outputfile:
            fieldnames = ['Title', 'Women Count', 'Men Count', 'Undefined Count', 'First Author is Woman', 'Last Author is Woman']
            writer = csv.DictWriter(outputfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in spamreader:
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
                print(f"{i} - Encontrou: {women_count} mulheres, {men_count} homens e {undefined_count} indeterminados.")

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