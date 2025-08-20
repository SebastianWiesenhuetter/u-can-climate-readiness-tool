# tools/import_from_excel.py
import os, sys, uuid, datetime as dt, re, math
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.dialects.mysql import insert as mysql_insert

# --- Load .env (../.env relative to this file) and build DATABASE_URL ---
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
except Exception:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME")
    if not all([DB_USER, DB_PASS, DB_NAME]):
        raise SystemExit("Missing DB env vars. Provide DATABASE_URL or DB_USER/DB_PASS/DB_NAME.")
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- City mapping (sheet label -> backend city_id string) ---
CITY_MAP = {
    "Lviv": "lviv",
    "Kyiv": "kyiv",
    "Zhytomyr": "zhytomyr",
    "Khmelnytskyi": "khmelnytskyi",
    "Ivano Frankivsk": "ivano-frankivsk",
    "Vinnytsia": "vinnytsia",
}

# Header row index (0-based). Your headers are on the 3rd row.
HEADER_ROW_INDEX = 2

# Column name canonicalization
def canon(col: str) -> str:
    # lowercase, strip, replace spaces/hyphens, collapse underscores
    c = re.sub(r"[\s\-]+", "_", str(col or "").strip().lower())
    # common variants
    c = c.replace("subcriterion", "sub_criterion")
    c = c.replace("sub__", "sub_")
    c = re.sub(r"_+", "_", c)
    return c

# Identify question lookup column on questions table (external code)
CANDIDATE_QUESTION_CODE_COLS = ["external_id", "code", "sub_criterion_id", "criterion_code", "question_code"]

def now_utc():
    return dt.datetime.utcnow()

def new_session_id():
    return uuid.uuid4().hex

def guess_city_id(sheet_name: str):
    # Prefer explicit mapping
    if sheet_name in CITY_MAP:
        return CITY_MAP[sheet_name]
    # If already using backend IDs as sheet names, accept directly
    if sheet_name in CITY_MAP.values():
        return sheet_name
    # Numeric ids allowed (if you ever use them)
    try:
        int(sheet_name)
        return sheet_name
    except Exception:
        return None  # => skip

def coerce_score(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return None

def read_sheet_long(path: str, sheet: str) -> pd.DataFrame:
    """Read a sheet with header on row 3 and normalize columns."""
    df = pd.read_excel(path, sheet_name=sheet, header=HEADER_ROW_INDEX, engine="openpyxl")
    # Canonicalize headers
    df.columns = [canon(c) for c in df.columns]
    # Map expected fields
    # We only really need sub_criterion_id and score
    # Accept a few variants just in case
    rename_map = {}
    for possible in ["criterion_id", "criterionid"]:
        if possible in df.columns: rename_map[possible] = "criterion_id"
    for possible in ["criterion"]:
        if possible in df.columns: rename_map[possible] = "criterion"
    for possible in ["sub_criterion_id", "subcriterion_id", "sub_criterionid"]:
        if possible in df.columns: rename_map[possible] = "sub_criterion_id"
    for possible in ["definition"]:
        if possible in df.columns: rename_map[possible] = "definition"
    for possible in ["scale"]:
        if possible in df.columns: rename_map[possible] = "scale"
    for possible in ["score", "value", "rating"]:
        if possible in df.columns: rename_map[possible] = "score"
    for possible in ["justification"]:
        if possible in df.columns: rename_map[possible] = "justification"
    for possible in ["references", "refs"]:
        if possible in df.columns: rename_map[possible] = "references"

    df = df.rename(columns=rename_map)

    # Keep only relevant columns (others are fine to exist)
    needed = {"sub_criterion_id", "score"}
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns on sheet '{sheet}': {missing}")

    # Drop fully empty rows; normalize score
    df["score"] = df["score"].apply(coerce_score)
    df = df[~df["score"].isna()]
    # Also drop rows where sub_criterion_id is empty
    df = df[df["sub_criterion_id"].astype(str).str.strip() != ""]
    return df

def build_question_lookup(conn, questions_tbl):
    """
    Returns (pk_col, pk_is_int, lookup_by_code_dict or None).
    If answers.question_id expects int but Excel has string codes,
    we'll translate via this dict using first matching code column.
    """
    # Detect primary key column name/type
    pk_cols = [c for c in questions_tbl.columns if c.primary_key]
    pk = pk_cols[0] if pk_cols else questions_tbl.c.id  # fallback
    pk_is_int = hasattr(pk.type, "python_type") and pk.type.python_type is int

    # Find a usable "code" column on questions
    code_col = None
    for name in CANDIDATE_QUESTION_CODE_COLS:
        if name in questions_tbl.c:
            code_col = questions_tbl.c[name]
            break

    if not code_col:
        return pk, pk_is_int, None

    # Build mapping code -> pk
    rows = conn.execute(select(code_col, pk)).all()
    code_map = {}
    for code, pkval in rows:
        if code is None: continue
        code_map[str(code).strip()] = pkval
    return pk, pk_is_int, code_map

def resolve_question_id(raw_sub_id, pk_is_int, code_map):
    s = str(raw_sub_id).strip()
    if code_map:
        if s in code_map:
            return code_map[s]
        # Try also without spaces
        s2 = re.sub(r"\s+", "", s)
        if s2 in code_map:
            return code_map[s2]
    # Otherwise, try to coerce directly (works if Excel already has numeric PKs)
    if pk_is_int:
        try:
            return int(float(s))  # handles "12" or "12.0"
        except Exception:
            return None
    else:
        return s or None

def main(xlsx_path: str):
    engine = create_engine(DATABASE_URL, future=True)
    md = MetaData()
    answers = Table("answers", md, autoload_with=engine)
    sessions = Table("response_sessions", md, autoload_with=engine)
    # Optional: questions for id lookup
    questions = Table("questions", md, autoload_with=engine)

    with engine.begin() as conn:
        # Find how to look up questions
        q_pk, q_pk_is_int, q_code_map = build_question_lookup(conn, questions)

        xls = pd.ExcelFile(xlsx_path, engine="openpyxl")
        total_sessions = 0
        total_answers = 0
        skipped_sheets = []
        for sheet in xls.sheet_names:
            city_id = guess_city_id(sheet)
            if city_id is None:
                print(f"[{sheet}] skipped (no city mapping)")
                skipped_sheets.append(sheet)
                continue

            try:
                df = read_sheet_long(xlsx_path, sheet)
            except Exception as e:
                print(f"[{sheet}] error parsing: {e}")
                continue

            if df.empty:
                print(f"[{sheet}] no scored rows → skipped")
                continue

            # Create one session per sheet
            session_id = new_session_id()
            conn.execute(
                sessions.insert().values(
                    session_id=session_id,
                    respondent_ref=f"import:{sheet}",
                    city_id=city_id,
                    created_at=now_utc(),
                )
            )
            total_sessions += 1

            # Prepare answer rows
            rows, bad_qids = [], []
            for _, r in df.iterrows():
                qid = resolve_question_id(r["sub_criterion_id"], q_pk_is_int, q_code_map)
                if qid is None:
                    bad_qids.append(str(r["sub_criterion_id"]))
                    continue
                val = coerce_score(r["score"])
                if val is None:
                    continue
                rows.append({
                    "session_id": session_id,
                    "question_id": qid,
                    "city_id": city_id,
                    "value": float(val),
                    "created_at": now_utc(),
                })

            if bad_qids:
                uniq = sorted(set(bad_qids))
                sample = ", ".join(uniq[:10]) + (" …" if len(uniq) > 10 else "")
                print(f"[{sheet}] warning: {len(bad_qids)} rows with unknown Sub-criterion_Id. Examples: {sample}")

            if not rows:
                print(f"[{sheet}] no valid answers after mapping → skipped")
                continue

            stmt = mysql_insert(answers).values(rows)
            ondup = stmt.on_duplicate_key_update(
                value=stmt.inserted.value,
                created_at=stmt.inserted.created_at
            )
            conn.execute(ondup)
            total_answers += len(rows)

            print(f"[{sheet}] OK → city_id={city_id}, session={session_id}, answers={len(rows)}")

        print(f"Done. Sessions created: {total_sessions}, answers upserted: {total_answers}")
        if skipped_sheets:
            print(f"Skipped sheets (no city mapping): {', '.join(skipped_sheets)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tools/import_from_excel.py /path/to/workbook.xlsx")
        sys.exit(1)
    main(sys.argv[1])
