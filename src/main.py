from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

STAGES = ["Lead", "Qualified", "Demo", "Proposal", "Closed Won", "Closed Lost"]

def load_data() -> pd.DataFrame:
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "data" / "sample.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find CSV at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Clean / ensure types
    df["deal_value"] = pd.to_numeric(df["deal_value"], errors="coerce").fillna(0)
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    df["close_date"] = pd.to_datetime(df["close_date"], errors="coerce")

    return df

def ensure_reports_folder() -> Path:
    base_dir = Path(__file__).resolve().parent.parent
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    return reports_dir

def print_summary(df: pd.DataFrame) -> None:
    print("\n--- PIPELINE SUMMARY ---")
    print(f"Total records: {len(df)}\n")

    counts = df["stage"].value_counts()
    for s in STAGES:
        print(f"{s:12} : {int(counts.get(s, 0))}")

    won = df[df["stage"] == "Closed Won"]
    lost = df[df["stage"] == "Closed Lost"]
    closed = len(won) + len(lost)

    win_rate = (len(won) / closed) if closed else 0
    revenue = won["deal_value"].sum()

    print("\n--- WIN / LOSS ---")
    print(f"Closed deals: {closed}")
    print(f"Win rate: {win_rate:.2%}")
    print(f"Revenue (won): {revenue:.0f}")

def plot_stage_counts(df: pd.DataFrame, reports_dir: Path) -> None:
    counts = df["stage"].value_counts()
    ordered_counts = [int(counts.get(s, 0)) for s in STAGES]

    plt.figure()
    plt.bar(STAGES, ordered_counts)
    plt.xticks(rotation=30, ha="right")
    plt.title("Leads by Stage")
    plt.tight_layout()
    out = reports_dir / "01_stage_counts.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print("Saved:", out)

def plot_closed_revenue(df: pd.DataFrame, reports_dir: Path) -> None:
    won = df[df["stage"] == "Closed Won"].copy()
    if won.empty:
        print("No Closed Won deals to plot revenue.")
        return

    # Revenue by close month
    won["close_month"] = won["close_date"].dt.to_period("M").astype(str)
    rev = won.groupby("close_month")["deal_value"].sum().sort_index()

    plt.figure()
    plt.plot(rev.index, rev.values, marker="o")
    plt.xticks(rotation=30, ha="right")
    plt.title("Closed-Won Revenue by Month")
    plt.tight_layout()
    out = reports_dir / "02_closed_won_revenue_by_month.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print("Saved:", out)

def plot_win_loss_pie(df: pd.DataFrame, reports_dir: Path) -> None:
    closed = df[df["stage"].isin(["Closed Won", "Closed Lost"])]
    if closed.empty:
        print("No closed deals to plot win/loss.")
        return

    counts = closed["stage"].value_counts()
    labels = counts.index.tolist()
    sizes = counts.values.tolist()

    plt.figure()
    plt.pie(sizes, labels=labels, autopct="%1.1f%%")
    plt.title("Win vs Loss")
    plt.tight_layout()
    out = reports_dir / "03_win_loss_pie.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print("Saved:", out)

def main():
    df = load_data()
    reports_dir = ensure_reports_folder()

    print_summary(df)

    # Charts
    plot_stage_counts(df, reports_dir)
    plot_closed_revenue(df, reports_dir)
    plot_win_loss_pie(df, reports_dir)

if __name__ == "__main__":
    main()