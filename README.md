# Women_in_BPM
Este projeto utiliza metadados de artigos acadêmicos (extraídos de ferramentas como Zotero) e APIs de gênero (como NamSor, que permite um grande número de consultas grátis) para quantificar e qualificar a participação de mulheres na pesquisa científica.
Apesar do foco inicial em Business Process Management (BPM), a solução é adaptável a qualquer área do conhecimento e pode ser estendida para análises de diversidade além do gênero feminino.

## Estrutura
pasta_principal/  
│  
├── 📄 assess_gender_pedro_namsor.py       # Processa os artigos científicos e determina o gênero dos autores. 
├── 📄 assess_gender_pedro.py              # Script Python para API Genderize.io 
├── 📄 assess_gender_pedro_genderapi.py    # Script Python para API Gender API
├── 📄 assess_gender_pedro_nameapi.py      # Script Python para API NameAPI
├── 📄 womenLib.csv                        # Dataset principal em CSV  
├── 📄 womenLibrary.bib                    # Bibliografia (formato BibTeX)  
│  
├── 📁 .vscode/                            # Configurações da IDE (ignorar)  
│   └── 📄 settings.json                   # Configurações específicas do VSCode  
│  
├── 📁 minuzzo/                            # Arquivos legados da pesquisadora Thayna Minuzzo  
│   ├── 📄 assess_gender.py                # Versão anterior do código Script Python (referência)  
│   ├── 📄 generate_insights_authors.py    # Gera estatísticas sobre autores por ano (referência) 
│   ├── 📄 scatter_map.py                  # Gera um mapa de dispersão com localizações (parece incompleto; referência) 
│   ├── 📄 send_authors_data.py            # Envia os dados processados para um servidor Elasticsearch (referência) 
│   ├── 📄 send_files.py                   # Envia os dados processados para um servidor Elasticsearch (referência) 
│   └── 📄 wordcould.csv                   # Cria uma nuvem de palavras com as tags manuais dos artigos (referência; deveria ser wordcloud.py) 
│  
├── 📁 auxiliar/                           # Arquivos auxiliares para encontrar dados extra
│   ├── 📄 count_names.py                  # Encontra quantas repetições de nomes há no arquivo .csv
│   ├── 📄 names_pedro.py                  # Cria uma lista de todos os primeiros nomes do arquivo .csv  
│   └── 📄 names.csv                       # Lista de nomes retornada pelo script names_pedro.py  
│
└── 📁 assessed/                           # Resultados processados pela aplicação  
    ├── 📄 Authors_{timestamp}.csv         # Análise do gênero para cada autor 
    ├── 📄 LibAssessed_{timestamp}.csv     # Análise numérica de gênero por artigo
    ├── 📄 YearlyReport_{timestamp}.csv    # Análise numérica de gênero dos autores por ano
    └── 📄 gender_cache.json               # Registro nomes acessados anteriormente para economia de recursos 

## Como Usar?
### Pré-requisitos
- Python 3.x
- Dependências: requests, unidecode, csv, json
- Chave de Autenticação NamSor (Obtenha em https://www.namsor.com/)

### Execução
1. Extrair dados do Zotero (exportar para CSV)
2. Processar os artigos:
python assess_gender_pedro_namsor.py [-h] [-i INPUT] -k KEY
- INPUT: nome do arquivo csv extraído do Zotero
- KEY: chave de autenticação NamSor

## Detalhes das Pastas
### .vscode/ (Ignorar)
Gerada automaticamente pelo Visual Studio Code. Contém configurações locais da IDE.

### minuzzo/ (Legado)
Arquivos da pesquisadora Thayna Minuzzo, mantidos para referência histórica ou comparação.

### assessed/ (Saídas)
Gerada automaticamente durante a execução. Armazena:
- Resultados processados.
- Logs de execução.
- Cache de nomes.
