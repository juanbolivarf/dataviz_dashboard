@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Normalizar nombres de columnas:
    # - quitar espacios
    # - quitar paréntesis
    # - quitar símbolo %
    # - pasar a minúsculas
    # - eliminar "_" al final
    new_cols = []
    for c in df.columns:
        nc = c.strip().lower()
        nc = nc.replace("(", "").replace(")", "")
        nc = nc.replace("%", "")
        nc = nc.replace(" ", "_")
        nc = nc.rstrip("_")
        new_cols.append(nc)
    df.columns = new_cols

    # Ahora deberíamos tener:
    # year, term, applications, admitted, enrolled,
    # retention_rate, student_satisfaction,
    # engineering_enrolled, business_enrolled,
    # arts_enrolled, science_enrolled

    # ⚠️ SOLO normalizamos si la columna realmente existe
    if "term" in df.columns:
        df["term"] = df["term"].astype(str).str.strip().str.title()

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # Asegurar tipos numéricos en métricas clave
    numeric_cols = [
        "applications", "admitted", "enrolled",
        "retention_rate", "student_satisfaction",
        "engineering_enrolled", "business_enrolled",
        "arts_enrolled", "science_enrolled",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
