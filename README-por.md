# Women_in_BPM
Este projeto utiliza metadados de artigos acadêmicos (extraídos de ferramentas como Zotero) e APIs de gênero (como NamSor, que permite um grande número de consultas grátis) para quantificar e qualificar a participação de mulheres na pesquisa científica.
Apesar do foco inicial em Business Process Management (BPM), a solução é adaptável a qualquer área do conhecimento e pode ser estendida para análises de diversidade além do gênero feminino.

## Estrutura
```
pasta_principal/
│
├── 📄 assess_gender_namsor.py             # Versão principal que processa artigos usando Namsor API
├── 📄 womenLib.csv                        # Base de dados principal (exportada do Zotero)
├── 📄 womenLibrary.bib                    # Referências bibliográficas no formato BibTeX
│
├── 📁 .vscode/                            # [IGNORAR] Configurações do ambiente de desenvolvimento
│   └── 📄 settings.json                   # Configurações específicas do VSCode
│
├── 📁 minuzzo/                            # Código legado da pesquisadora Thayna Minuzzo
│   ├── 📄 assess_gender.py                # Versão original do processamento de gênero
│   ├── 📄 generate_insights_authors.py    # Gera estatísticas de autores por ano
│   ├── 📄 scatter_map.py                  # Mapa de dispersão (em desenvolvimento)
│   ├── 📄 send_authors_data.py            # Exportação para ElasticSearch (autores)
│   ├── 📄 send_files.py                   # Exportação para ElasticSearch (artigos)
│   └── 📄 wordcould.py                    # Nuvem de palavras das tags manuais
│
├── 📁 under_construction/                 # Ferramentas em processo de construção
│   ├── 📄 assess_gender_genderize.py      # Versão alternativa usando Genderize.io API
│   ├── 📄 assess_gender_genderapi.py      # Versão alternativa usando Gender API
│   ├── 📄 assess_gender_nameapi.py        # Versão alternativa usando NameAPI
│   └── 📄 create_worldmap.py              # Utiliza APIs para descobrir a localização dos artigos
│
├── 📁 auxiliar/                           # Ferramentas de suporte
│   ├── 📄 count_names.py                  # Conta frequência de nomes na base
│   ├── 📄 names_pedro.py                  # Extrai lista de primeiros nomes
│   ├── 📄 names.csv                       # Saída do names_pedro.py
│   ├── 📄 create_worldcloud.py            # Cria uma nuvem de palavras
│   ├── 📄 create_worldmap_no_api.py       # Busca informações de países para criar um mapa
│   └── 📄 generate_graphs.py              # Automatizamente gera uma série de gráficos comparativos
│
└── 📁 assessed/                           # Resultados das análises
    ├── 📄 Authors_*.csv                   # Dados completos por autor (timestamp)
    ├── 📄 LibAssessed_*.csv               # Metadados processados por artigo
    ├── 📄 YearlyReport_*.csv              # Estatísticas anuais de gênero
    └── 📄 gender_cache.json               # Cache de consultas a APIs
```
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
