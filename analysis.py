import sqlite3
import pandas as pd
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu, false_discovery_control

DB_PATH = "cell-count.db"

def get_summary_table():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT sample_id, population, count FROM cell_counts", conn)
    conn.close()

    df["total_count"] = df.groupby("sample_id")["count"].transform("sum")
    df["percentage"] = df["count"] / df["total_count"] * 100

    df = df.rename(columns = {"sample_id": "sample"})
    df = df[["sample", "total_count", "population", "count", "percentage"]]

    return df

def get_melanoma_miraclib_pbmc():
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            cc.sample_id, 
            cc.population,
            cc.count,
            s.subject_id,
            subj.response
        FROM cell_counts AS cc
        JOIN samples AS s   ON cc.sample_id = s.sample_id
        JOIN subjects AS subj ON s.subject_id = subj.subject_id 
        WHERE subj.condition = 'melanoma'
            AND subj.treatment = 'miraclib'
            AND s.sample_type = 'PBMC'
            AND subj.response IN ('yes', 'no')
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["total_count"] = df.groupby("sample_id")["count"].transform("sum")
    df["percentage"] = df["count"] / df["total_count"] * 100
    return df

def make_boxplot():
    df = get_melanoma_miraclib_pbmc()

    plt.figure(figsize=(10, 6))
    sns.boxplot(data = df, x = "population", y = "percentage", hue = "response")

    plt.title("Cell population relative frequency: responders vs non-responders\n(melanoma, miraclib, PBMC)")
    plt.xlabel("Cell population")
    plt.ylabel("Relative frequency (%)")
    plt.legend(title = "Response")
    plt.tight_layout()

    os.makedirs("outputs", exist_ok = True)
    plt.savefig("outputs/boxplot_responders_vs_nonresponders.png", dpi = 150)
    plt.close()
    print("Saved outputs/boxplot_responders_vs_nonresponders.png")

def run_stats():
    df = get_melanoma_miraclib_pbmc()

    populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    results = []

    for pop in populations:
        responders = df[(df["population"] == pop) & (df["response"] == "yes")]["percentage"]
        non_responders = df[(df["population"] == pop) & (df["response"] == "no")]["percentage"]

        stat, p_value = mannwhitneyu(responders, non_responders, alternative = "two-sided")

        results.append({
            "population": pop,
            "responder_median": responders.median(),
            "non_responder_median": non_responders.median(),
            "p_value": p_value,

        })
    results_df = pd.DataFrame(results)

    results_df["p_value_corrected"] = false_discovery_control(
        results_df["p_value"], method = "bh"
    )

    results_df["significant"] = results_df["p_value_corrected"] < 0.05
    
    return results_df

def get_baseline_cohort():
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            s.sample_id,
            s.subject_id,
            subj.project_id,
            subj.response,
            subj.sex
        FROM samples AS s
        JOIN subjects AS subj ON s.subject_id = subj.subject_id
        WHERE subj.condition = 'melanoma'
            AND subj.treatment = 'miraclib'
            AND s.sample_type = 'PBMC'
            AND s.time_from_treatment_start = 0
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_baseline_breakdowns():
    df = get_baseline_cohort()

    by_project = df["project_id"].value_counts()

    subjects = df.drop_duplicates("subject_id")
    by_response = subjects["response"].value_counts()
    by_sex = subjects["sex"].value_counts()

    return by_project, by_response, by_sex

def get_avg_bcell_melanoma_males():
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT AVG(cc.count) AS avg_b_cell
        FROM cell_counts AS cc
        JOIN samples AS s ON cc.sample_id = s.sample_id
        JOIN subjects AS subj ON s.subject_id = subj.subject_id
        WHERE subj.condition = 'melanoma'
            AND subj.sex = 'M'
            AND subj.response = 'yes'
            AND s.time_from_treatment_start = 0
            AND cc.population = 'b_cell'
    """

    result = pd.read_sql_query(query, conn)
    conn.close()
    return result["avg_b_cell"].iloc[0]

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok = True)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    summary = get_summary_table()

    summary.to_csv("outputs/summary_table.csv", index = False)
    print("Saves outputs/summary_table.csv -", len(summary), "rows")
    
    one_sample = summary[summary["sample"] == "sample00000"]
    print(one_sample)
    print("Percentages sum to:", one_sample["percentage"].sum())

    print("\nTotal rows:", len(summary))

    mel = get_melanoma_miraclib_pbmc()
    print(mel.head(10))
    one = mel[mel["sample_id"] == mel["sample_id"].iloc[0]]
    print("\nOne sample's percentages sum to:", one["percentage"].sum())

    print("Rows:", len(mel), "| unique samples:", mel["sample_id"].nunique())
    print("Response counts:\n", mel["response"].value_counts())

    make_boxplot()

    stats = run_stats()
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    print(stats)

    stats.to_csv("outputs/stats_results.csv", index = False)
    print("Saved outputs/stats_results.csv")

    cohort = get_baseline_cohort()
    print("Baseline cohort - samples:", len(cohort),
          "| subjects:", cohort["subject_id"].nunique())
    
    by_project, by_response, by_sex = get_baseline_breakdowns()
    print("\nSamples per project:\n", by_project)
    print("\nResponders / non-responders:\n", by_response)
    print("\nMales / females:\n", by_sex)

    avg_bcell = get_avg_bcell_melanoma_males()
    print(f"\nAvg B cells (melanoma males, responders, time = 0): {avg_bcell:.2f}")

    # Save Part 4 outputs
    by_project, by_response, by_sex = get_baseline_breakdowns()
    by_project.to_csv("outputs/part4_samples_per_project.csv", header = ["count"])
    by_response.to_csv("outputs/part4_response_breakdown.csv", header = ["count"])
    by_sex.to_csv("outputs/part4_sex_breakdown.csv", header = ["count"])
    
    avg_bcell = get_avg_bcell_melanoma_males()
    with open("outputs/part4_avg_bcell.txt", "w") as f:
        f.write(f"Average B cells (melanoma males, responders, time = 0): {avg_bcell:.2f}\n")