print("=" * 55)
print("  HBASE SERVING LAYER — WIKI CONTENTION STORE")
print("=" * 55)

hbase_table = {}

def put(row_key, column_family, column, value):
    if row_key not in hbase_table:
        hbase_table[row_key] = {}
    hbase_table[row_key][f"{column_family}:{column}"] = value

def get(row_key):
    return hbase_table.get(row_key, {})

def scan(limit=None):
    rows = list(hbase_table.items())
    return rows[:limit] if limit else rows

articles = [
    ("Wikipedia:Reference desk/Miscellaneous", "350400", "extreme"),
    ("Talk:Intelligent design",                "33151",  "extreme"),
    ("Talk:Israel",                            "30088",  "extreme"),
    ("India",                                  "29381",  "extreme"),
    ("United Kingdom",                         "28672",  "extreme"),
    ("World War II",                           "28283",  "extreme"),
    ("Britney Spears",                         "27786",  "extreme"),
    ("George Washington",                      "26140",  "high"),
    ("The Beatles",                            "25562",  "high"),
    ("European Union",                         "24990",  "high"),
]

print("\n[PUT] Loading contested articles into HBase...\n")
for title, edits, tier in articles:
    put(title, "meta",  "title",      title)
    put(title, "stats", "edit_count", edits)
    put(title, "stats", "tier",       tier)
    print(f"  PUT '{title}' -> edit_count={edits}, tier={tier}")

print("\n[GET] Instant lookup — single article:\n")
row = get("India")
for col, val in row.items():
    print(f"  {col:30s} = {val}")

print("\n[SCAN] All extreme contention articles:\n")
print(f"  {'Article':<45} {'Edits':>8}  {'Tier'}")
print(f"  {'-'*45} {'-'*8}  {'-'*8}")
for key, cols in scan():
    if cols.get("stats:tier") == "extreme":
        print(f"  {key:<45} {cols.get('stats:edit_count', ''):>8}  {cols.get('stats:tier', '')}")

print("\n[SUMMARY]")
print(f"  Total rows in HBase table : {len(hbase_table)}")
print(f"  Extreme contention        : {sum(1 for _, c in scan() if c.get('stats:tier') == 'extreme')}")
print(f"  High contention           : {sum(1 for _, c in scan() if c.get('stats:tier') == 'high')}")
print("\nHBase simulation complete.")
