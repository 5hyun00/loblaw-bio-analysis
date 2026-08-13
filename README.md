# LobLaw Complete Analysis README

Hello, This ReadME should help everything run smoothly.

## Project Scope
This project loads immune-cell clinical trial data into a SQLite database and analyzes how melanoma patients respond to miraclib treatment. I did this by statistically analyzing the population frequencies using boxplots, Mann-Whitney U test with Benjamini-Hochberg correction to rigorously test which differences were statistically significant. There is also an interactive dashboard included into this project so the data is much easier to overview.

## How to run - 3 commands
From the repository root, run:
```
make setup       #installs dependencies
make pipeline    #builds database + generates all outputs
make dashboard   #launches the dashboard
```

## Database schema
The database consists of a hierarchy of four tables in this order:
- projects
- subjects
- samples
- cell_counts

This is because attributes such as condition, treatment, and response were consistent per subject so I placed them in the subjects table to avoid repeating those attributes across each subject's 3 samples. 
Cell_counts is in long format because adding a new cell population means new rows, not a change in the table.
Because there are thousands of samples, this normalized design avoids data duplication and keeps the data consistent. To keep queries fast as the data grows, I would add indexes on the columns that I filter on most (like condition, treatment, response, and sample_type), so the database can jump straight to matching rows instead of scanning every one. Each table connects to the one above it through foreign keys. For example, samples reference their subject and cell_counts reference their sample.

## Code structure
- `load_data.py` 
    - helps to build the schema and load the CSV into the database
- `analysis.py`
    - contains all of the functions that query the database and saves all of the outputs in main
    - all outputs land in a separate folder named "outputs/"
- `app.py`
    - this file puts it all together by taking the functions made in analysis.py and displaying the data in an interactive dashboard

Note: the CSV's actual column names differ slightly from the assignment description (e.g. `condition` rather than indication), so the code follows the real column names in the file


