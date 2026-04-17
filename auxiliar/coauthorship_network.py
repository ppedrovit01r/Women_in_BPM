import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import itertools

# 1. Load Data
df = pd.read_csv('curated_authors.csv')

# 2. Strict Gender Categorization
def categorize(row):
    if row['Probability'] < 0.75:
        return 'unknown'
    elif str(row['Gender']).lower() == 'female':
        return 'female'
    elif str(row['Gender']).lower() == 'male':
        return 'male'
    return 'unknown'

df['Category'] = df.apply(categorize, axis=1)

# Filter ONLY WOMEN
df_female = df[df['Category'] == 'female'].copy()

# 3. Name Formatting and Anonymization
def format_name(name_str):
    if pd.isna(name_str): return ""
    parts = name_str.split(',')
    if len(parts) == 2:
        return f"{parts[1].strip()} {parts[0].strip()}"
    return name_str

def anonymize_name(name_str):
    if pd.isna(name_str): return ""
    parts = name_str.split(',')
    if len(parts) == 2:
        first = parts[1].strip()
        last = parts[0].strip()
        return f"{first[0] if first else ''}. {last[0] if last else ''}."
    return name_str[:2]

df_female['Full_Name'] = df_female['Author Name'].apply(format_name)
df_female['Initials'] = df_female['Author Name'].apply(anonymize_name)

# 4. Map Articles to Authors
article_to_authors = {}
article_cols = [c for c in df_female.columns if c.startswith('Article_')]

for _, row in df_female.iterrows():
    author = row['Author Name']
    for col in article_cols:
        article = row[col]
        if pd.isna(article) or article == '$':
            continue
        if article not in article_to_authors:
            article_to_authors[article] = []
        article_to_authors[article].append(author)

# 5. Build the Graph (Female Only)
G_female = nx.Graph()

for _, row in df_female.iterrows():
    G_female.add_node(row['Author Name'], 
                      full_name=row['Full_Name'],
                      initials=row['Initials'],
                      pub_count=row['Publication_Count'])

for authors in article_to_authors.values():
    if len(authors) > 1:
        for u, v in itertools.combinations(authors, 2):
            if G_female.has_edge(u, v):
                G_female[u][v]['weight'] += 1
            else:
                G_female.add_edge(u, v, weight=1)

# 6. Filter for Visualization
# Remove isolated nodes (women who did not co-author with other women)
G_sub = G_female.subgraph([n for n, d in G_female.degree() if d > 0])

print(f"Total women in dataset: {G_female.number_of_nodes()}")
print(f"Women who co-authored with other women: {G_sub.number_of_nodes()}")
print(f"Total connections among women: {G_sub.number_of_edges()}")

# For visualization, we take nodes with degree >= 2 to avoid clutter if the graph is too large
if G_sub.number_of_nodes() > 500:
    core_nodes = [n for n, d in G_sub.degree() if d >= 2]
    G_viz = G_sub.subgraph(core_nodes)
    print(f"Main network (Degree >= 2) for visualization: {G_viz.number_of_nodes()} nodes")
else:
    G_viz = G_sub

# 7. Visual Configuration
pos = nx.spring_layout(G_viz, k=0.3, iterations=50, seed=42)
node_sizes = [G_viz.nodes[n]['pub_count'] * 50 for n in G_viz.nodes()]

# --- PLOT 1: Full Names ---
labels_full = {n: G_viz.nodes[n]['full_name'] for n in G_viz.nodes()}
plt.figure(figsize=(24, 18))
nx.draw_networkx_edges(G_viz, pos, alpha=0.3, edge_color='gray')
nx.draw_networkx_nodes(G_viz, pos, node_color='#e377c2', node_size=node_sizes, edgecolors='white', linewidths=1)
nx.draw_networkx_labels(G_viz, pos, labels=labels_full, font_size=9, font_color='black', 
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=0.5))
plt.title("Female-Only BPM Co-authorship Network (Full Names)", fontsize=24)
plt.axis('off')
plt.tight_layout()
plt.savefig('female_coauthorship_full.png', dpi=150)
plt.close()

# --- PLOT 2: Anonymized Initials ---
labels_anon = {n: G_viz.nodes[n]['initials'] for n in G_viz.nodes()}
plt.figure(figsize=(24, 18))
nx.draw_networkx_edges(G_viz, pos, alpha=0.3, edge_color='gray')
nx.draw_networkx_nodes(G_viz, pos, node_color='#e377c2', node_size=node_sizes, edgecolors='white', linewidths=1)
nx.draw_networkx_labels(G_viz, pos, labels=labels_anon, font_size=9, font_color='black', 
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=0.5))
plt.title("Female-Only BPM Co-authorship Network (Anonymized)", fontsize=24)
plt.axis('off')
plt.tight_layout()
plt.savefig('female_coauthorship_anon.png', dpi=150)
plt.close()

print("Files saved successfully!")