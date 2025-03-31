import csv

def parse_valid_name(name):
    # Remove espaços desnecessários e pega apenas o primeiro nome (antes do primeiro espaço)
    name = name.strip()
    return name.split(' ')[0]

def main():
    with open('womenLib.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile)
        with open('names.csv', 'w', newline='', encoding='utf-8') as outputfile:
            fieldnames = ['Index', 'First Name']
            writer = csv.DictWriter(outputfile, fieldnames=fieldnames)
            writer.writeheader()

            for index, row in enumerate(spamreader):
                # Verifica se a linha tem pelo menos 4 colunas
                if len(row) >= 4:
                    authors = row[3].split(';')  # Assume que os autores estão na 4ª coluna (índice 3)
                    for author in authors:
                        if ',' in author:
                            # Extrai o primeiro nome após a vírgula
                            first_name = author.split(', ')[1].split(' ')[0]
                            first_name = parse_valid_name(first_name)
                            writer.writerow({
                                'Index': index,
                                'First Name': first_name
                            })
                else:
                    print(f"Aviso: A linha {index} não tem colunas suficientes. Ignorando...")

if __name__ == "__main__":
    main()