import pandas as pd
import numpy as np
import os

def run_analysis():
    # --- 1. Load and Explore (4 marks) ---
    input_file = "data/trends_clean.csv"
    
    # Check if file exists before loading
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Please run Task 2 first.")
        return

    # Load into DataFrame
    df = pd.read_csv(input_file)
    
    print("--- First 5 Rows of Cleaned Data ---")
    print(df.head())
    
    print(f"\nShape of DataFrame: {df.shape}")
    
    # Calculate averages using Pandas
    avg_score_val = df['score'].mean()
    avg_comments_val = df['num_comments'].mean()
    print(f"Average Score: {avg_score_val:.2f}")
    print(f"Average Comments: {avg_comments_val:.2f}\n")

    # --- 2. Basic Analysis with NumPy (8 marks) ---
    # Converting columns to NumPy arrays for specific math operations
    scores_array = df['score'].values
    comments_array = df['num_comments'].values

    print("--- NumPy Statistical Analysis ---")
    print(f"Mean Score: {np.mean(scores_array):.2f}")
    print(f"Median Score: {np.median(scores_array)}")
    print(f"Standard Deviation: {np.std(scores_array):.2f}")
    print(f"Highest Score: {np.max(scores_array)}")
    print(f"Lowest Score: {np.min(scores_array)}")

    # Category with most stories (using Pandas mode which utilizes NumPy logic)
    most_common_category = df['category'].mode()[0]
    print(f"Category with most stories: {most_common_category}")

    # Identify story with most comments using NumPy argmax
    max_comments_idx = np.argmax(comments_array)
    top_story_title = df.iloc[max_comments_idx]['title']
    top_story_count = df.iloc[max_comments_idx]['num_comments']
    print(f"Story with most comments: '{top_story_title}' ({top_story_count} comments)\n")

    # --- 3. Add New Columns (5 marks) ---
    # Formula: engagement = num_comments / (score + 1)
    # Adding 1 to denominator prevents "Division by Zero" errors
    df['engagement'] = df['num_comments'] / (df['score'] + 1)

    # Formula: is_popular = True if score > average score
    df['is_popular'] = df['score'] > avg_score_val

    # --- 4. Save the Result (3 marks) ---
    output_file = "data/trends_analysed.csv"
    
    # Ensure the data directory exists just in case
    if not os.path.exists('data'):
        os.makedirs('data')
        
    df.to_csv(output_file, index=False)
    
    print("--- Task 3 Complete ---")
    print(f" Successfully saved updated analysis to {output_file}")
    print(f"New columns 'engagement' and 'is_popular' added to {len(df)} rows.")

if __name__ == "__main__":
    run_analysis()
