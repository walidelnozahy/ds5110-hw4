# Short Assignment 7A: Windows and Plans

Starter repository for HW4 (DS 5110, Week 7, Lecture 7A).
The handout, `HW4.pdf`, (SEE CANVAS FOR ASSINGMENT) has the tasks and the grading.

## Run it

1. Download the course reference `movielens.db` from Canvas and copy it into
   `data/` (it is git-ignored), or set `MOVIELENS_DB` to its path. It has the
   schema used in the Week 7 slides and notebook. `run.py` checks the schema
   first and tells you if a table or column is missing.
2. Write each query in `sql/`, replacing `-- YOUR QUERY HERE`.
3. Run one task at a time, or all of them:

```bash
python run.py t1
python run.py all
```

`run.py` needs only Python 3.10+ and pandas. It opens the database read-only;
Task 4 works on a copy in `output/`. Results go to `output/`, and
`WRITEUP.md` (CREATE THE WRITEUP.MD FILE) quotes them.

## Layout

| Path | What it is | Yours to edit? |
| --- | --- | --- |
| `run.py` | runs the SQL, checks shapes, writes `output/` | no |
| `sql/*.sql` | one file per query | yes |


## Use of AI assistants

Record here what you used an assistant for, and for what:

- Claude helped me draft the SQL in `sql/`. I went through every line and can explain it.
- With the professor's permission, Claude also helped write the predictions and explanations in `WRITEUP.md`. Predictions were committed before each task was run.
