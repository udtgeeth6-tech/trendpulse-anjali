#task4-visualization
import pandas as pd
import matplotlib.pyplot as plt
import os

def run_visualization():
    # --- Task 1: Setup (2 marks) ---
    input_file = "data/trends_analysed.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Please run Task 3 first.")
        return

    # Load the analysed data
    df = pd.read_csv(input_file)
    
    # Create output directory
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created {output_dir}/ folder.")

    # --- Task 2: Chart 1 - Top 10 Stories by Score (6 marks) ---
    plt.figure(figsize=(10, 6))
    
    # Sort and take top 10
    top_10 = df.nlargest(10, 'score').sort_values('score', ascending=True)
    
    # Shorten titles longer than 50 characters
    display_titles = [t[:47] + "..." if len(t) > 50 else t for t in top_10['title']]
    
    plt.barh(display_titles, top_10['score'], color='skyblue')
    plt.title('Top 10 Stories by Score')
    plt.xlabel('Score')
    plt.ylabel('Story Title')
    plt.tight_layout()
    
    plt.savefig(f"{output_dir}/chart1_top_stories.png")
    plt.close() # Close to free memory and avoid overlapping in dashboard
    print("Saved Chart 1: Top 10 Stories")

    # --- Task 3: Chart 2 - Stories per Category (6 marks) ---
    plt.figure(figsize=(8, 6))
    
    cat_counts = df['category'].value_counts()
    # Using a list of distinct colors
    colors = ['gold', 'lightgreen', 'coral', 'lightskyblue', 'orchid']
    
    cat_counts.plot(kind='bar', color=colors[:len(cat_counts)])
    plt.title('Distribution of Stories per Category')
    plt.xlabel('Category')
    plt.ylabel('Number of Stories')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(f"{output_dir}/chart2_categories.png")
    plt.close()
    print("Saved Chart 2: Stories per Category")

    # --- Task 4: Chart 3 - Score vs Comments (6 marks) ---
    plt.figure(figsize=(8, 6))
    
    # Split data for legend coloring
    popular = df[df['is_popular'] == True]
    not_popular = df[df['is_popular'] == False]
    
    plt.scatter(not_popular['score'], not_popular['num_comments'], 
                alpha=0.6, label='Not Popular', c='gray')
    plt.scatter(popular['score'], popular['num_comments'], 
                alpha=0.8, label='Popular', c='crimson', edgecolors='black')
    
    plt.title('Score vs. Number of Comments')
    plt.xlabel('Score')
    plt.ylabel('Comments')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    plt.savefig(f"{output_dir}/chart3_scatter.png")
    plt.close()
    print("Saved Chart 3: Score vs Comments")

    # --- Bonus: Dashboard Figure (Combining them) ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('TrendPulse Data Analysis Dashboard', fontsize=20)

    # Subplot 1: Top Stories
    axes[0, 0].barh(display_titles, top_10['score'], color='skyblue')
    axes[0, 0].set_title('Top 10 Stories')

    # Subplot 2: Category Bar
    cat_counts.plot(kind='bar', color=colors[:len(cat_counts)], ax=axes[0, 1])
    axes[0, 1].set_title('Stories per Category')

    # Subplot 3: Scatter Plot
    axes[1, 0].scatter(not_popular['score'], not_popular['num_comments'], alpha=0.5, c='gray')
    axes[1, 0].scatter(popular['score'], popular['num_comments'], alpha=0.7, c='crimson')
    axes[1, 0].set_title('Score vs Comments')
    axes[1, 0].set_xlabel('Score')
    axes[1, 0].set_ylabel('Comments')

    # Subplot 4: Summary Table (Empty or basic text)
    axes[1, 1].axis('off')
    summary_text = (
        f"Total Stories: {len(df)}\n"
        f"Avg Score: {df['score'].mean():.1f}\n"
        f"Most Active: {cat_counts.index[0]}\n"
        f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d')}"
    )
    axes[1, 1].text(0.5, 0.5, summary_text, fontsize=14, ha='center', va='center', 
                    bbox=dict(facecolor='white', alpha=0.5))

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f"{output_dir}/dashboard.png")
    plt.close()
    
    print("--- Task 4 Complete ---")
    print(f" All 3 charts and the dashboard saved to the '{output_dir}/' folder.")

if __name__ == "__main__":
    run_visualization()
