# Women_in_BPM
Este repositório fornece um pipeline automatizado para quantificar e qualificar a participação de mulheres na pesquisa científica. Aproveitando metadados bibliográficos (exportados de gerenciadores de referência como o Zotero) e APIs de inferência de gênero (principalmente NamSor), esta ferramenta extrai e analisa a demografia de autoria.

Embora originalmente adaptada para mapear a comunidade acadêmica de Gestão de Processos de Negócio (BPM), a arquitetura é altamente adaptável a qualquer domínio de conhecimento e pode ser estendida para analisar outros fatores demográficos.

## Estrutura
```
main_folder/
│
├── 📄 assess_gender_namsor.py       # Script principal de execução (integração com a API NamSor)
├── 📄 womenLib.csv                  # Banco de dados principal de metadados (exportação do Zotero)
├── 📄 womenLibrary.bib              # Referências bibliográficas (formato BibTeX)
│
├── 📁 assessed/                     # Diretório de saída (Gerado automaticamente)
│   ├── Authors_*.csv                # Dados completos extraídos dos autores
│   ├── LibAssessed_*.csv            # Metadados dos artigos processados
│   ├── YearlyReport_*.csv           # Estatísticas anuais de gênero e tendências
│   └── gender_cache.json            # Cache local para minimizar chamadas de API
│
└── 📁 auxiliary/                    # Ferramentas de suporte para extração e visualização de dados
    ├── 📄 names_extract.py          # Extrai primeiros nomes distintos
    ├── 📄 generate_graphs.py        # Gera gráficos comparativos automaticamente
    ├── 📄 process_authors.py        # Garante que não haja autores duplicados no arquivo
    ├── 📄 coauthorship_network.py   # Cria uma rede de coautoria
    ├── 📄 cochran.py                # Realiza o cálculo de Cochran e atribui automaticamente
                                     o número apropriado de autores com base no arquivo original.
    ├── 📄 countries.py              # Cria mapas mundiais com informações anotadas manualmente.
    └── 📄 create_worldcloud.py      # Gera nuvens de palavras temáticas
```
## Como Usar?
### Pré-requisitos
- Python 3.x
- Dependências: requests, unidecode, csv, json
- Chave de Autenticação NamSor (Obtenha em https://www.namsor.com/)

### Execução Principal
1. Prepare seus dados
Exporte sua biblioteca bibliográfica do Zotero (ou ferramentas similares) no formato CSV e coloque-a no diretório raiz.

2. Execute o script principal de processamento
Execute o script principal via terminal, passando seu arquivo de entrada e sua chave da API NamSor como argumentos:
```python assess_gender_namsor.py -i womenLib.csv -k SUA_CHAVE_DA_API```
- -i : O nome do seu arquivo CSV de entrada contendo os metadados dos artigos.
- -k : Sua chave de autenticação NamSor.

3. Acesse seus resultados
Assim que a execução for concluída, navegue até a pasta assessed/. O script gerará arquivos CSV com carimbo de data/hora contendo os autores categorizados, bibliotecas processadas e um relatório anual resumido da distribuição de gênero.

---

## Apoio e Contato

Este projeto foi desenvolvido e é mantido como parte das iniciativas do **BPM Research Lab @UFRGS** (Laboratório de Pesquisa em Gestão de Processos de Negócios da Universidade Federal do Rio Grande do Sul).

Acompanhe nossas pesquisas, publicações e o desenvolvimento de novas ferramentas focadas na comunidade acadêmica e industrial de BPM:
* 📸 **Instagram:** [@bpmlabufrgs](https://www.instagram.com/bpmlabufrgs/)