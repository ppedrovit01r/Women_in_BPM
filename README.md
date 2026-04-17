# Women_in_BPM
This repository provides an automated pipeline to quantify and qualify women's participation in scientific research. By leveraging bibliographic metadata (exported from reference managers like Zotero) and gender-inference APIs (primarily NamSor), this tool extracts and analyzes authorship demographics. 

While originally tailored to map the Business Process Management (BPM) academic community, the architecture is highly adaptable to any knowledge domain and can be extended to analyze other demographic factors.

## Structure
```
main_folder/
│
├── 📄 assess_gender_namsor.py       # Main execution script (NamSor API integration)
├── 📄 womenLib.csv                  # Main metadata database (Zotero export)
├── 📄 womenLibrary.bib              # Bibliographic references (BibTeX format)
│
├── 📁 assessed/                     # Output directory (Auto-generated)
│   ├── Authors_*.csv                # Complete extracted author data
│   ├── LibAssessed_*.csv            # Processed article metadata
│   ├── YearlyReport_*.csv           # Annual gender statistics and trends
│   └── gender_cache.json            # Local cache to minimize API calls
│
└── 📁 auxiliary/                    # Support tools for data extraction & visualization
    ├── 📄 names_extract.py          # Extracts distinct first names
    ├── 📄 generate_graphs.py        # Automatically generates comparative charts
    ├── 📄 process_authors.py        # Make sure there are no duplicate authors in the file
    ├── 📄 coauthorship_network.py   # Creates a co-authorship network
    ├── 📄 cochran.py                # It performs the Cochran calculation and automatically assigns
                                     the appropriate number of authors based on the original file.
    ├── 📄 countries.py              # Creates world maps with manually annotated information.
    └── 📄 create_worldcloud.py      # Generates topical word clouds
```
## How to Use?
### Prerequisites
- Python 3.x
- Dependencies: requests, unidecode, csv, json
- NamSor Authentication Key (Get it at https://www.namsor.com/)

### Main Execution
1. Prepare your data
Export your bibliographic library from Zotero (or similar tools) in CSV format and place it in the root directory.
2. Run the main processing script
Execute the primary script via terminal, passing your input file and your NamSor API key as arguments:
```python assess_gender_namsor.py -i womenLib.csv -k YOUR_API_KEY```
- -i : The name of your input CSV file containing the article metadata.
- -k : Your NamSor authentication key.
3. Access your results
Once the execution is complete, navigate to the assessed/ folder. The script will generate timestamped CSV files containing the categorized authors, processed libraries, and a summarized yearly report of the gender distribution.

---

## Support and Contact

This project was developed and is maintained as part of the initiatives of the **BPM Research Lab @UFRGS** (Business Process Management Research Laboratory of the Federal University of Rio Grande do Sul).

Follow our research, publications, and the development of new tools focused on the academic and industrial BPM community:

* 📸 **Instagram:** [@bpmlabufrgs](https://www.instagram.com/bpmlabufrgs/)