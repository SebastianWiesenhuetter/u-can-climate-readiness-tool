import os, math, yaml
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
print (BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")
XLSX_PATH = os.path.join(DATA_DIR, "UKR_questionaire_V2a.xlsx")
MAP_PATH  = os.path.join(DATA_DIR, "questionnaire.mapping.yaml")

# DB creds
load_dotenv(os.path.join(BASE_DIR, ".env"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def is_number(x):
    return isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x))

def load_mapping():
    with open(MAP_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def read_title_subtitle(xlsx_path, sheet, title_cell=None, subtitle_cell=None):
    if not (title_cell or subtitle_cell):
        return None, None
    raw = pd.read_excel(xlsx_path, sheet_name=sheet, header=None, dtype=str)
    def get_cell(rc):
        if not rc: return None
        r, c = rc.get("row"), rc.get("col")
        try:
            val = raw.iat[r, c]
            return None if (pd.isna(val) or str(val).strip() == "") else str(val).strip()
        except Exception:
            return None
    return get_cell(title_cell), get_cell(subtitle_cell)

def main():
    cfg = load_mapping()
    sheet = cfg.get("sheet", "Questionnaire")
    header_row = cfg.get("header_row", 2)
    cols = cfg["columns"]
    defaults = cfg.get("defaults", {})
    scale_min_default = int(defaults.get("scale_min", 0))
    scale_max_default = int(defaults.get("scale_max", 5))

    # 1) Title/subtitle from raw sheet (optional)
    title, subtitle = read_title_subtitle(
        XLSX_PATH, sheet,
        cfg.get("title_cell"), cfg.get("subtitle_cell")
    )

    # 2) Read the real table with a fixed header row
    df = pd.read_excel(
        XLSX_PATH,
        sheet_name=sheet,
        header=header_row,
        dtype=str
    )

    # 3) Forward-fill category id and name
    df[cols["category_id"]]   = df[cols["category_id"]].ffill()
    df[cols["category_name"]] = df[cols["category_name"]].ffill()

    # 4) Keep only rows that look like real questions
    df["_sub_num"] = pd.to_numeric(df[cols["sub_index"]], errors="coerce")
    df = df[df["_sub_num"].apply(is_number)]
    df = df[df[cols["question_text"]].notna() & (df[cols["question_text"]].astype(str).str.strip() != "")]

    # 5) Normalize to DB shape
    out = pd.DataFrame({
        "category_id":     pd.to_numeric(df[cols["category_id"]], errors="coerce").astype("Int64"),
        "category_name":   df[cols["category_name"]].astype(str).str.strip(),
        "sub_index":       df["_sub_num"].astype(int),
        "sub_name":        df.get(cols.get("sub_name", ""), "").fillna("").astype(str).str.strip()
                           if cols.get("sub_name") else "",
        "question_text":   df[cols["question_text"]].astype(str).str.strip(),
        "scale_min":       scale_min_default,
        "scale_max":       scale_max_default,
        "option_labels":   df.get(cols.get("option_labels", ""), "").fillna("").astype(str)
                           if cols.get("option_labels") else "",
        "references_text": df.get(cols.get("references_text", ""), "").fillna("").astype(str)
                           if cols.get("references_text") else "",
        "source_links":    df.get(cols.get("source_links", ""), "").fillna("").astype(str)
                           if cols.get("source_links") else "",
    })
    out = out[out["category_id"].notna()].copy()
    out["category_id"] = out["category_id"].astype(int)

    engine = create_engine(DATABASE_URL)

    # Ensure tables
    create_questions_sql = """
    CREATE TABLE IF NOT EXISTS questions (
      id INT AUTO_INCREMENT PRIMARY KEY,
      category_id     INT NOT NULL,
      category_name   VARCHAR(255) NOT NULL,
      sub_index       INT NOT NULL,
      sub_name        VARCHAR(255),
      question_text   TEXT NOT NULL,
      scale_min       INT NOT NULL DEFAULT 0,
      scale_max       INT NOT NULL DEFAULT 5,
      option_labels   TEXT,
      references_text TEXT,
      source_links    TEXT,
      UNIQUE KEY uq_cat_sub (category_id, sub_index)
    );
    """
    create_meta_sql = """
    CREATE TABLE IF NOT EXISTS questionnaire_meta (
      id INT PRIMARY KEY,
      title TEXT,
      subtitle TEXT,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    # upsert_q_sql = text("""
    # INSERT INTO questions
    #   (category_id, category_name, sub_index, question_text, scale_min, scale_max, option_labels, references_text, source_links)
    # VALUES
    #   (:category_id, :category_name, :sub_index, :question_text, :scale_min, :scale_max, :option_labels, :references_text, :source_links)
    # ON DUPLICATE KEY UPDATE
    #   category_name   = VALUES(category_name),
    #   question_text   = VALUES(question_text),
    #   option_labels   = VALUES(option_labels),
    #   references_text = VALUES(references_text),
    #   source_links    = VALUES(source_links),
    #   scale_min       = VALUES(scale_min),
    #   scale_max       = VALUES(scale_max);
    # """)
    upsert_q_sql = text("""
    INSERT INTO questions
    (category_id, category_name, sub_index, sub_name, question_text, scale_min, scale_max, option_labels, references_text, source_links)
    VALUES
    (:category_id, :category_name, :sub_index, :sub_name, :question_text, :scale_min, :scale_max, :option_labels, :references_text, :source_links)
    ON DUPLICATE KEY UPDATE
    category_name   = VALUES(category_name),
    sub_name        = VALUES(sub_name),
    question_text   = VALUES(question_text),
    option_labels   = VALUES(option_labels),
    references_text = VALUES(references_text),
    source_links    = VALUES(source_links),
    scale_min       = VALUES(scale_min),
    scale_max       = VALUES(scale_max);
    """)

    upsert_meta_sql = text("""
    INSERT INTO questionnaire_meta (id, title, subtitle)
    VALUES (1, :title, :subtitle)
    ON DUPLICATE KEY UPDATE
      title = VALUES(title),
      subtitle = VALUES(subtitle);
    """)

    with engine.begin() as conn:
        conn.execute(text(create_questions_sql))
        conn.execute(text(create_meta_sql))
        conn.execute(text("SET NAMES utf8mb4;"))
        conn.execute(text("SET CHARACTER SET utf8mb4;"))

        # upsert questions
        for _, row in out.iterrows():
            conn.execute(upsert_q_sql, row.to_dict())

        # upsert title/subtitle (if present)
        conn.execute(upsert_meta_sql, {
            "title": title or "",
            "subtitle": subtitle or ""
        })

    print(f"Imported/updated {len(out)} questions")
    if title or subtitle:
        print(f"Stored meta: title='{title or ''}' | subtitle='{subtitle or ''}'")

if __name__ == "__main__":
    main()
