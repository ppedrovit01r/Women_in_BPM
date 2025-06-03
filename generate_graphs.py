import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


sns.set(style="whitegrid")

# Use colorblind-friendly palette
COLORS = sns.color_palette("colorblind")

def get_timestamp_from_user():
    """Prompt user for timestamp in YYYYMMDD_HHMM format with default"""
    default_timestamp = "20250411_1612"
    
    while True:
        timestamp = input(f"Enter timestamp in YYYYMMDD_HHMM format [default: {default_timestamp}]: ") or default_timestamp
        try:
            # Validate timestamp format
            datetime.strptime(timestamp, "%Y%m%d_%H%M")
            return timestamp
        except ValueError:
            print(f"Invalid format. Please use YYYYMMDD_HHMM format or press Enter for default ({default_timestamp}).")

def load_data(timestamp):
    """Load both Report and LibAssessed files"""
    report_file = f"assessed/Report_{timestamp}.csv"
    lib_file = f"assessed/LibAssessed_{timestamp}.csv"
    
    try:
        report_df = pd.read_csv(report_file)
        lib_df = pd.read_csv(lib_file)
        
        # Remove TOTAL rows if they exist
        report_df = report_df[report_df['Year'].astype(str) != 'TOTAL']
        lib_df = lib_df[lib_df['Year'].astype(str) != 'TOTAL']
        
        # Convert Year to integer
        report_df['Year'] = report_df['Year'].astype(int)
        lib_df['Year'] = lib_df['Year'].astype(int)
        
        return report_df, lib_df
    except FileNotFoundError as e:
        print(f"Error: {e.filename} not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def get_year_range(df):
    """Get the min and max years from the data and prompt user for range"""
    min_year = df['Year'].min()
    max_year = df['Year'].max()
    
    print(f"Data available from {min_year} to {max_year}")
    while True:
        try:
            start_year = int(input(f"Enter start year ({min_year}-{max_year}): "))
            end_year = int(input(f"Enter end year ({start_year}-{max_year}): "))
            
            if min_year <= start_year <= end_year <= max_year:
                return start_year, end_year
            else:
                print("Invalid range. Please try again.")
        except ValueError:
            print("Please enter valid years.")

def annotate_bar(ax, bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)


def plot_absolute_numbers_pie(df, year_range):
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

    total_male = filtered_df['Male Authors'].sum()
    total_female = filtered_df['Female Authors'].sum()
    total_unknown = filtered_df['Unknown Gender Authors'].sum()
    total_authors = total_male + total_female + total_unknown

    labels = [f'Male ({total_male})', f'Female ({total_female})', f'Unknown ({total_unknown})']
    sizes = [total_male, total_female, total_unknown]

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,
                                      colors=[COLORS[0], COLORS[1], COLORS[2]], wedgeprops=dict(width=1))
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    ax.set_title(f"Gender Distribution of Authors ({year_range[0]}–{year_range[1]})\nTotal: {total_authors} authors", pad=20)
    plt.show()


def plot_gender_authorship(lib_df, year_range):
    """
    Plot gender authorship distribution with calculated categories:
    - Only men
    - Only women
    - Equal men/women
    - More men than women
    - More women than men
    """
    # Filter data by year range
    filtered_df = lib_df[(lib_df['Year'] >= year_range[0]) & 
                       (lib_df['Year'] <= year_range[1])].copy()
    
    # Initialize counters
    categories = {
        'Only men': 0,
        'Only women': 0,
        'Equal men/women': 0,
        'More men than women': 0,
        'More women than men': 0
    }
    
    # Calculate categories for each article
    for _, row in filtered_df.iterrows():
        male = row['Male Authors']
        female = row['Female Authors']
        total = male + female
        
        # Skip articles with only unknown authors
        if total == 0:
            continue
            
        if female == 0:
            categories['Only men'] += 1
        elif male == 0:
            categories['Only women'] += 1
        elif male == female:
            categories['Equal men/women'] += 1
        elif male > female:
            categories['More men than women'] += 1
        else:
            categories['More women than men'] += 1
    
    total_articles = sum(categories.values())
    
    # Create DataFrame for visualization
    plot_data = pd.DataFrame({
        'Category': categories.keys(),
        'Count': categories.values(),
        'Percentage': [count/total_articles*100 for count in categories.values()]
    }).sort_values('Count', ascending=False)
    
    # Color palette
    color_mapping = {
        'Only men': COLORS[0],      
        'Only women': COLORS[1],      
        'Equal men/women': COLORS[2],
        'More men than women': COLORS[4],  
        'More women than men': COLORS[5]  
    }
    
    # Create figure
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    ax = plt.subplot(111)
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        plot_data['Count'],
        labels=plot_data.apply(lambda x: f"{x['Category']}\n({x['Count']})", axis=1),
        colors=[color_mapping[c] for c in plot_data['Category']],
        autopct=lambda p: f'{p:.1f}%',
        startangle=180,
        textprops={'fontsize': 10},
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
        pctdistance=0.8
    )
    
    # Style percentage text
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
        if float(autotext.get_text().replace('%', '')) > 5:
            autotext.set_color('white')
    
    # Add title
    ax.set_title(
        f"Gender Authorship Distribution ({year_range[0]}-{year_range[1]})\nTotal Articles: {total_articles}",
        pad=20,
        fontsize=14,
        fontweight='bold'
    )
    
    # Add legend with percentages
    legend_labels = [f"{row['Category']} ({row['Percentage']:.1f}%)" 
                    for _, row in plot_data.iterrows()]
    plt.legend(
        wedges,
        legend_labels,
        title="Categories",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=10
    )
    
    plt.tight_layout()
    plt.show()


def plot_absolute_numbers_bar(df, year_range):
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    years = filtered_df['Year']

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(years, filtered_df['Total Authors'], color='lightgray', label='Total Authors', alpha=0.6)
    ax.bar(years, filtered_df['Male Authors'], color=COLORS[0], label='Male Authors')
    ax.bar(years, filtered_df['Female Authors'], bottom=filtered_df['Male Authors'], color=COLORS[1], label='Female Authors')

    for i in range(len(filtered_df)):
        total = filtered_df.iloc[i]['Total Authors']
        male = filtered_df.iloc[i]['Male Authors']
        female = filtered_df.iloc[i]['Female Authors']
        year = filtered_df.iloc[i]['Year']
        ax.text(year, total + 2, f"{int(total)}", ha='center', fontsize=8)
        ax.text(year, male / 2, f"{int(male)}", ha='center', fontsize=8, color='white')
        ax.text(year, male + female / 2, f"{int(female)}", ha='center', fontsize=8, color='white')

    ax.set_title(f"Absolute Number of Authors by Gender ({year_range[0]}–{year_range[1]})")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Authors")
    ax.legend()
    plt.xticks(years, rotation=45)
    plt.tight_layout()
    plt.show()


def plot_gender_distribution_stacked(df, year_range):
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])].copy()
    filtered_df['Total'] = filtered_df['Male Authors'] + filtered_df['Female Authors']
    filtered_df['Male %'] = filtered_df['Male Authors'] / (filtered_df['Male Authors'] + filtered_df['Female Authors'])
    filtered_df['Female %'] = 1 - filtered_df['Male %']

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(filtered_df['Year'], filtered_df['Male %'], color=COLORS[0], label='Male')
    ax.bar(filtered_df['Year'], filtered_df['Female %'], bottom=filtered_df['Male %'], color=COLORS[1], label='Female')

    for i in range(len(filtered_df)):
        year = filtered_df.iloc[i]['Year']
        male_pct = filtered_df.iloc[i]['Male %']
        female_pct = filtered_df.iloc[i]['Female %']
        male = int(round(filtered_df.iloc[i]['Male Authors']))
        female = int(round(filtered_df.iloc[i]['Female Authors']))
        ax.text(year, male_pct / 2, f"{male}\n{male_pct*100:.1f}%", ha='center', va='center', color='white', fontsize=9, fontweight='bold')
        ax.text(year, male_pct + female_pct / 2, f"{female}\n{female_pct*100:.1f}%", ha='center', va='center', color='white', fontsize=9, fontweight='bold')

    ax.axhline(0.75, color='black', linestyle='dotted', linewidth=1, label='75%')
    ax.axhline(0.5, color='black', linestyle='--', linewidth=1, label='50%')
    ax.axhline(0.25, color='black', linestyle='dotted', linewidth=1, label='25%')
    ax.set_ylim(0, 1)
    ax.set_ylabel('Percentage')
    ax.set_title(f'Gender Distribution of Authors ({year_range[0]}–{year_range[1]})')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(filtered_df['Year'], rotation=45)
    plt.tight_layout()
    plt.show()


def plot_first_last_author_distribution(df, year_range, author_type='first'):
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])].copy()

    if author_type == 'first':
        col = 'Articles with female first author'
        label = 'First'
    else:
        col = 'Articles with female last author'
        label = 'Last'

    filtered_df['Female %'] = filtered_df[col] / filtered_df['Total Articles']
    filtered_df['Male %'] = 1 - filtered_df['Female %']

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(filtered_df['Year'], filtered_df['Male %'], color=COLORS[0], label=f'Male {label} Author')
    ax.bar(filtered_df['Year'], filtered_df['Female %'], bottom=filtered_df['Male %'], color=COLORS[1], label=f'Female {label} Author')

    for i in range(len(filtered_df)):
        year = filtered_df.iloc[i]['Year']
        female = filtered_df.iloc[i][col]
        total = filtered_df.iloc[i]['Total Articles']
        male = total - female
        male_pct = filtered_df.iloc[i]['Male %']
        female_pct = filtered_df.iloc[i]['Female %']
        ax.text(year, male_pct / 2, f"{int(round(male))}\n{male_pct*100:.1f}%", ha='center', va='center', color='white', fontsize=8, fontweight='bold')
        ax.text(year, male_pct + female_pct / 2, f"{int(round(female))}\n{female_pct*100:.1f}%", ha='center', va='center', color='white', fontsize=8, fontweight='bold')

    ax.axhline(0.75, color='black', linestyle='dotted', linewidth=1, label='75%')
    ax.axhline(0.5, color='black', linestyle='--', linewidth=1, label='50%')
    ax.axhline(0.25, color='black', linestyle='dotted', linewidth=1, label='25%')
    ax.set_ylim(0, 1)
    ax.set_ylabel('Percentage')
    ax.set_title(f'Gender Distribution of {label} Authors ({year_range[0]}–{year_range[1]})')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.xticks(filtered_df['Year'], rotation=45)
    plt.tight_layout()
    plt.show()


def main():
    # Ask for file path
    timestamp = get_timestamp_from_user()
    # Load both files
    report_df, lib_df = load_data(timestamp)
    if report_df is None or lib_df is None:
        return
    
    # Get year range from user
    year_range = get_year_range(report_df)
    
    # Create all visualizations
    plot_absolute_numbers_pie(report_df, year_range)
    plot_gender_authorship(lib_df, year_range)
    plot_absolute_numbers_bar(report_df, year_range)
    plot_gender_distribution_stacked(report_df, year_range)
    plot_first_last_author_distribution(report_df, year_range, author_type='first')
    plot_first_last_author_distribution(report_df, year_range, author_type='last')

if __name__ == "__main__":
    main()