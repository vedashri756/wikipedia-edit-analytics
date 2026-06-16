from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, desc

spark = SparkSession.builder \
    .appName("EditStormDetector") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Load contributor stats as a stream simulation
edits = spark.read \
    .option("delimiter", "\t") \
    .csv("/wiki/output/edit_counts") \
    .toDF("article_title", "edit_count") \
    .withColumn("edit_count", col("edit_count").cast("int"))

# Detect storms: articles with edit count over 1000 (proxy for contested articles)
print("\n========== EDIT STORM CANDIDATES ==========")
print("Articles with 1000+ edits (high contention / storm-prone)\n")

storms = edits.filter(col("edit_count") > 1000) \
    .orderBy(desc("edit_count"))

storms.show(30, truncate=False)

# RDD demonstration
print("\n========== RDD ANALYSIS: CONTENTION TIERS ==========")
rdd = edits.rdd

extreme = rdd.filter(lambda r: r[1] and int(r[1]) > 10000).count()
high    = rdd.filter(lambda r: r[1] and 5000 < int(r[1]) <= 10000).count()
medium  = rdd.filter(lambda r: r[1] and 1000 < int(r[1]) <= 5000).count()
low     = rdd.filter(lambda r: r[1] and int(r[1]) <= 1000).count()

print(f"  Extreme contention (>10,000 edits) : {extreme} articles")
print(f"  High contention    (5,000-10,000)  : {high} articles")
print(f"  Medium contention  (1,000-5,000)   : {medium} articles")
print(f"  Low contention     (<1,000)        : {low} articles")

print("\nDone.")
spark.stop()
