# trendpulse-anjali
A data pipeline project where you fetch live trending data.
Load data/trends_analysed.csv into a DataFrame
Create a folder called outputs/ if it doesn't exist
Use plt.savefig() before any plt.show() on all charts
Combine all 3 charts into one figure:

Use plt.subplots(1, 3) or plt.subplots(2, 2) to lay them out together
Add an overall title: "TrendPulse Dashboard"
Save as outputs/dashboard.png



**The mini project 4 pipeline is created and executed successfully**
import ipywidgets as widgets
from IPython.display import display, clear_output

steps = [
    "Step 1: Task 1 generates the JSON file.",
    "Step 2: Task 2 cleans the JSON and makes a CSV.",
    "Step 3: Task 3 calculates the statistics.",
    "Step 4: Task 4 creates the final Dashboard!"
]

button = widgets.Button(description="Show Next Step")
output = widgets.Output()
counter = 0

def on_button_clicked(b):
    global counter
    with output:
        if counter < len(steps):
            print(steps[counter])
            counter += 1
        else:
            print(" All steps completed!")

button.on_click(on_button_clicked)
display(button, output)
output :
 Show Next StepStep 1: Task 1 generates the JSON file.
Step 2: Task 2 cleans the JSON and makes a CSV.
Step 3: Task 3 calculates the statistics.
Step 4: Task 4 creates the final Dashboard!
** All steps completed!**
<img width="1600" height="1200" alt="dashboard (1)" src="https://github.com/user-attachments/assets/3484da00-5270-4e3d-8d16-f92d2211d585" />

