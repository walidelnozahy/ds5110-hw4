"""Short Assignment 7A runner. Provided: do not edit.

    python run.py t1      # T1a, T1b, and T1c checked against the Week 6 chain
    python run.py t2      # both T2 files
    python run.py t3      # sessions (plus a default-frame variant) and running means
    python run.py t4      # plans, timings and size, before and after sql/t4_indexes.sql
    python run.py all     # everything, in order

Reads the course reference database at data/movielens.db (or the path in
MOVIELENS_DB): MovieLens 100k with the schema used in the Week 7 slides.
Never writes to it: Task 4 works on a copy in output/, which is git-ignored.
Every task writes its results to output/; WRITEUP.md quotes those files.
"""
import json
import os
import random
import re
import shutil
import sqlite3
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
SQL = ROOT / "sql"
OUT = ROOT / "output"
DB = Path(os.environ.get("MOVIELENS_DB", ROOT / "data" / "movielens.db"))

# The four queries the app team runs (Task 4). Do not change them.
APP_QUERIES = {
    "A_profile": "SELECT movie_id, rating, timestamp FROM ratings "
                 "WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20",
    "B_movie_page": "SELECT COUNT(*), AVG(rating) FROM ratings WHERE movie_id = ?",
    "C_recent": "SELECT COUNT(*) FROM ratings WHERE timestamp >= ?",
    "D_month": "SELECT COUNT(*) FROM ratings "
               "WHERE strftime('%Y-%m', timestamp, 'unixepoch') = ?",
}
N_RUNS = 500
MAX_INDEXES = 2


# ---------------------------------------------------------------- helpers
def connect():
    """Open the reference database read-only, so no task can change it."""
    if not DB.exists():
        sys.exit(f"Missing {DB}. Copy the course reference movielens.db there, "
                 "or set MOVIELENS_DB to its path.")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    check_schema(con)
    return con


REQUIRED_SCHEMA = {
    "ratings": {"user_id", "movie_id", "rating", "timestamp"},
    "users": {"user_id", "occupation"},
    "movies": {"movie_id", "title"},
    "movie_genres": {"movie_id", "genre_id"},
}


def check_schema(con):
    """Stop early, with a clear message, if the database has another schema."""
    problems = []
    for table, cols in REQUIRED_SCHEMA.items():
        have = {row[1] for row in con.execute(f"PRAGMA table_info({table})")}
        if not have:
            problems.append(f"table {table} is missing")
        elif cols - have:
            problems.append(f"{table} lacks columns {sorted(cols - have)}")
    if problems:
        sys.exit("This is not the course reference database: " + "; ".join(problems)
                 + ". Use movielens.db from Canvas (your HW3 schema may use other names).")


def read_sql_file(name):
    path = SQL / name
    text = path.read_text()
    body = re.sub(r"--.*", "", text).strip()
    if not body:
        sys.exit(f"{path.relative_to(ROOT)} has no query yet.")
    return text


def run_file(con, name):
    t0 = time.perf_counter()
    df = pd.read_sql_query(read_sql_file(name), con)
    return df, time.perf_counter() - t0


def plan_lines(con, sql, params=()):
    return [row[3] for row in con.execute("EXPLAIN QUERY PLAN " + sql, params)]


def save(name, obj):
    OUT.mkdir(exist_ok=True)
    path = OUT / name
    path.write_text(json.dumps(obj, indent=2, default=str))
    print(f"wrote {path.relative_to(ROOT)}")


def check(condition, message):
    if not condition:
        print(f"CHECK FAILED: {message}")
    return bool(condition)


def n_ratings(con):
    return con.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]


# ---------------------------------------------------------------- tasks
def t1():
    con = connect()
    a, secs = run_file(con, "t1a_rating_in_context.sql")
    need = {"user_id", "movie_id", "rating", "user_mean", "movie_mean"}
    ok = check(need <= set(a.columns), f"T1a columns must include {sorted(need)}")
    ok &= check(len(a) == n_ratings(con), "T1a must return one row per rating")
    OUT.mkdir(exist_ok=True)
    a.head(20).to_csv(OUT / "t1a_head.csv", index=False)
    b, _ = run_file(con, "t1b_above_both.sql")
    need_b = {"n_ratings", "n_above_both", "share_above_both", "share_above_both_20plus"}
    ok &= check(need_b <= set(b.columns) and len(b) == 1,
                f"T1b must return one row with columns {sorted(need_b)}")
    b.to_csv(OUT / "t1b.csv", index=False)
    print(b.to_string(index=False))

    chain, t_chain = run_file(con, "t1c_week6_chain.sql")
    rewrite, t_rewrite = run_file(con, "t1c_window_rewrite.sql")
    cols = ["genre_id", "movie_id", "movie_mean", "genre_mean"]
    ok &= check(set(cols) <= set(rewrite.columns), f"T1c columns must include {cols}")
    same = False
    if set(cols) <= set(rewrite.columns):
        norm = lambda d: (d[cols].round(9).sort_values(["genre_id", "movie_id"])
                          .reset_index(drop=True))
        same = len(chain) == len(rewrite) and norm(chain).equals(norm(rewrite))
    ok &= check(same, "T1c must return exactly the rows of the Week 6 chain")
    save("t1.json", {"t1a_rows": len(a), "t1a_seconds": round(secs, 3),
                     "t1a_plan": plan_lines(con, read_sql_file("t1a_rating_in_context.sql")),
                     "t1b": b.to_dict(orient="records"),
                     "t1c": {"rows_week6_chain": len(chain), "rows_rewrite": len(rewrite),
                             "same_rows": bool(same),
                             "seconds_week6_chain": round(t_chain, 4),
                             "seconds_rewrite": round(t_rewrite, 4)},
                     "checks_passed": ok})


def t2():
    con = connect()
    rn, _ = run_file(con, "t2_top3_row_number.sql")
    rk, _ = run_file(con, "t2_top3_rank.sql")
    OUT.mkdir(exist_ok=True)
    rn.to_csv(OUT / "t2_row_number.csv", index=False)
    rk.to_csv(OUT / "t2_rank.csv", index=False)
    n_occ = con.execute("SELECT COUNT(DISTINCT occupation) FROM users").fetchone()[0]
    ok = check("occupation" in rn.columns and "occupation" in rk.columns,
               "both T2 results need an occupation column")
    ok &= check(rn.groupby("occupation").size().max() <= 3,
                "ROW_NUMBER version: at most 3 rows per occupation")
    ok &= check(len(rk) >= len(rn), "RANK version should return at least as many rows")
    all_occ = {o for (o,) in con.execute("SELECT DISTINCT occupation FROM users")}
    missing = sorted(all_occ - set(rn["occupation"]))
    save("t2.json", {"occupations": n_occ, "rows_row_number": len(rn), "rows_rank": len(rk),
                     "occupations_with_fewer_than_3_rows": sorted(
                         o for o, n in rn.groupby("occupation").size().items() if n < 3),
                     "occupations_missing": missing, "checks_passed": ok})


def t3():
    con = connect()
    s, secs = run_file(con, "t3_sessions.sql")
    need = {"user_id", "session_no", "n_ratings"}
    ok = check(need <= set(s.columns), f"T3 columns must include {sorted(need)}")
    ok &= check(int(s["n_ratings"].sum()) == n_ratings(con),
                "T3: session sizes must add up to the number of ratings")
    OUT.mkdir(exist_ok=True)
    s.to_csv(OUT / "t3_sessions.csv", index=False)
    per_user = s.groupby("user_id").size()
    result = {"sessions": len(s), "seconds": round(secs, 3),
              "median_ratings_per_session": float(s["n_ratings"].median()),
              "max_ratings_per_session": int(s["n_ratings"].max()),
              "users_with_one_session": int((per_user == 1).sum()),
              "median_sessions_per_user": float(per_user.median())}
    # Same query with any ROWS frame removed: does the default frame change the answer?
    text = read_sql_file("t3_sessions.sql")
    variant = re.sub(r"ROWS\s+BETWEEN\s+UNBOUNDED\s+PRECEDING\s+AND\s+CURRENT\s+ROW", "",
                     text, flags=re.I)
    if variant != text:
        v = pd.read_sql_query(variant, con)
        same = len(v) == len(s) and v.reset_index(drop=True).equals(s.reset_index(drop=True))
        result["default_frame_variant_identical"] = bool(same)
    else:
        result["default_frame_variant_identical"] = "no ROWS frame found in your query"

    r, _ = run_file(con, "t3b_running_mean.sql")
    need_r = {"user_id", "movie_id", "timestamp", "rating", "run_default", "run_rows"}
    ok &= check(need_r <= set(r.columns), f"T3b columns must include {sorted(need_r)}")
    ok &= check(len(r) == n_ratings(con), "T3b must return one row per rating")
    if need_r <= set(r.columns):
        differ = (r["run_default"] - r["run_rows"]).abs() > 1e-9
        tied = r.duplicated(["user_id", "timestamp"], keep=False)
        last = (r.sort_values(["user_id", "timestamp", "movie_id"])
                 .groupby("user_id").tail(1))
        result["t3b"] = {
            "rows_where_frames_disagree": int(differ.sum()),
            "rows_sharing_a_timestamp_with_another_rating_of_that_user": int(tied.sum()),
            "disagreeing_rows_that_share_a_timestamp": int((differ & tied).sum()),
            "users_whose_last_values_agree": int(((last["run_default"] - last["run_rows"]).abs()
                                                  <= 1e-9).sum()),
            "users": int(r["user_id"].nunique()),
        }
        r[differ].head(20).to_csv(OUT / "t3b_disagreements_head.csv", index=False)
    result["checks_passed"] = ok
    save("t3.json", result)


def t4():
    work = OUT / "t4_work.db"
    OUT.mkdir(exist_ok=True)
    connect().close()                              # stops with a message if DB is missing
    shutil.copy(DB, work)
    con = sqlite3.connect(work)
    for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='index' "
                               "AND sql IS NOT NULL").fetchall():
        con.execute(f"DROP INDEX {name}")          # start from the reference schema
    con.execute("VACUUM")

    rng = random.Random(5110)
    users = [u for (u,) in con.execute("SELECT user_id FROM users")]
    movies = [m for (m,) in con.execute("SELECT movie_id FROM movies")]
    t_max = con.execute("SELECT MAX(timestamp) FROM ratings").fetchone()[0]
    params = {"A_profile": [(rng.choice(users),) for _ in range(N_RUNS)],
              "B_movie_page": [(rng.choice(movies),) for _ in range(N_RUNS)],
              "C_recent": [(t_max - rng.randint(1, 14) * 86400,) for _ in range(N_RUNS)]}
    months = [m for (m,) in con.execute(
        "SELECT DISTINCT strftime('%Y-%m', timestamp, 'unixepoch') FROM ratings ORDER BY 1")]
    picked = [rng.choice(months) for _ in range(N_RUNS)]
    params["D_month"] = [(m,) for m in picked]
    bounds = {m: con.execute("SELECT CAST(strftime('%s', ? || '-01') AS INTEGER), "
                             "CAST(strftime('%s', ? || '-01', '+1 month') AS INTEGER)",
                             (m, m)).fetchone() for m in months}
    params["D_rewrite"] = [bounds[m] for m in picked]
    queries = dict(APP_QUERIES)
    queries["D_rewrite"] = read_sql_file("t4d_month_range.sql").strip().rstrip(";")

    def size():
        pc = con.execute("PRAGMA page_count").fetchone()[0]
        ps = con.execute("PRAGMA page_size").fetchone()[0]
        return pc * ps

    def measure():
        out = {}
        for k, sql in queries.items():
            t0 = time.perf_counter()
            answers = [con.execute(sql, p).fetchall() for p in params[k]]
            out[k] = {"plan": plan_lines(con, sql, params[k][0]),
                      "ms_per_query": round(1000 * (time.perf_counter() - t0) / N_RUNS, 4),
                      "answers": answers}
        return out

    before, bytes_before = measure(), size()
    ddl = read_sql_file("t4_indexes.sql")
    n_idx = len(re.findall(r"CREATE\s+(UNIQUE\s+)?INDEX", re.sub(r"--.*", "", ddl), flags=re.I))
    if n_idx > MAX_INDEXES:
        sys.exit(f"T4: the budget is {MAX_INDEXES} indexes; t4_indexes.sql creates {n_idx}.")
    t0 = time.perf_counter()
    con.executescript(ddl)
    build_s = time.perf_counter() - t0
    after, bytes_after = measure(), size()

    report = {"indexes_created": n_idx, "index_build_seconds": round(build_s, 3),
              "db_bytes_before": bytes_before, "db_bytes_after": bytes_after,
              "queries": {}}
    ok = True
    ok &= check(after["D_rewrite"]["answers"] == after["D_month"]["answers"],
                "T4d: the range rewrite must return the same counts as D_month")
    report["d_rewrite_same_counts"] = after["D_rewrite"]["answers"] == after["D_month"]["answers"]
    for k in queries:
        same = before[k]["answers"] == after[k]["answers"]
        ok &= check(same, f"T4 {k}: answers changed after indexing")
        report["queries"][k] = {
            "plan_before": before[k]["plan"], "plan_after": after[k]["plan"],
            "ms_before": before[k]["ms_per_query"], "ms_after": after[k]["ms_per_query"],
            "speedup": round(before[k]["ms_per_query"] / max(after[k]["ms_per_query"], 1e-9), 1),
            "answers_unchanged": same}
    report["checks_passed"] = ok
    save("t4.json", report)
    for k, r in report["queries"].items():
        print(f"{k:13s} {r['ms_before']:9.3f} ms -> {r['ms_after']:9.3f} ms   {r['plan_after']}")


TASKS = {"t1": t1, "t2": t2, "t3": t3, "t4": t4}

if __name__ == "__main__":
    which = sys.argv[1:] or ["all"]
    for name in (TASKS if which == ["all"] else which):
        print(f"--- {name}")
        TASKS[name]()
