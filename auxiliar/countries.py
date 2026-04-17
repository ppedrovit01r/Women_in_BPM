import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

# 1. Load the original data
df = pd.read_csv('final_women_sample.csv')

# 2. Fix country names in the dataframe to match Natural Earth names
country_mapping = {
    'New Zeland': 'New Zealand', # or just check before in step 4
}
df['Country_Fixed'] = df['Country'].replace(country_mapping)

# 3. Aggregate stats by country
country_stats = df.groupby('Country_Fixed').agg(
    Authors=('Author Name', 'count'),
    Pubs=('Publication_Count', 'sum')
).reset_index()

# 4. Load the world map directly from the official source
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url)
#print(world['name'].unique())

# No dataset do Natural Earth, o nome do país fica na coluna 'NAME'.
# Ajustando nomes se necessário para o merge
world['NAME'] = world['NAME'].replace({
    'United States': 'United States of America', # you can change the country name in the map as well
    'Korea': 'South Korea'
})

# 5. Merge data with world map
world_data = world.merge(country_stats, left_on='NAME', right_on='Country_Fixed', how='left')
world_data['Authors'] = world_data['Authors'].fillna(0)
world_data['Pubs'] = world_data['Pubs'].fillna(0)

# 6. Reusable function to plot maps (with an option to toggle annotations)
def plot_annotated_map(column, title, filename, cmap):
    plt.close('all')
    fig, ax = plt.subplots(figsize=(20, 12))
    
    # Base map (light grey for countries with no data)
    world.plot(ax=ax, color='#f2f2f2', edgecolor='0.8')
    
    # Data layer (only plot countries with data > 0)
    active_countries = world_data[world_data[column] > 0].copy()
    
    active_countries.plot(
        column=column, 
        cmap=cmap, 
        linewidth=0.8, 
        ax=ax, 
        edgecolor='0.5', 
        legend=True,
        legend_kwds={'label': title, 'orientation': "horizontal", 'pad': 0.05, 'shrink': 0.5}
    )
    
    # Add labels if requested (using representative_point instead of centroid for better placement)
    active_countries['coords'] = active_countries['geometry'].representative_point().apply(lambda x: x.coords[0])
    
    for idx, row in active_countries.iterrows():
        label = f"{int(row[column])}"
        ax.annotate(
            text=label, 
            xy=row['coords'], 
            horizontalalignment='center', 
            fontsize=10, 
            fontweight='bold', 
            color='black',
            bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.6, ec='none')
        )

    ax.set_title(title, fontsize=20, pad=20)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    print(f"Successfully generated: {filename}")

# 7. Generate the required maps
plot_annotated_map('Authors', 'Number of Female Authors by Country (Annotated Sample)', 'authors_annotated.png', 'YlOrBr')
plot_annotated_map('Pubs', 'Total Publications by Female Authors by Country (Annotated Sample)', 'publications_annotated.png', 'Blues')

print("All maps generated successfully.")