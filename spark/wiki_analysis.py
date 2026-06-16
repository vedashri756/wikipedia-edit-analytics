from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round, desc

spark = SparkSession.builder \
    .appName("WikipediaAnalytics") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Load edit counts
article_edits = spark.read \
    .option("delimiter", "\t") \
    .csv("/wiki/output/edit_counts") \
    .toDF("article_title", "edit_count")

article_edits = article_edits.withColumn("edit_count", col("edit_count").cast("int"))

# Load contributor stats
contributors = spark.read \
    .option("delimiter", "\t") \
    .csv("/wiki/processed/clean_contributors") \
    .toDF("username", "total_edits", "total_reverts", "revert_ratio")

contributors = contributors \
    .withColumn("total_edits", col("total_edits").cast("int")) \
    .withColumn("total_reverts", col("total_reverts").cast("int")) \
    .withColumn("revert_ratio", col("revert_ratio").cast("float"))

# Register as SQL tables
article_edits.createOrReplaceTempView("article_edits")
contributors.createOrReplaceTempView("contributors")

print("\n========== TOP 20 MOST EDITED ARTICLES ==========")
spark.sql("""
    SELECT article_title, edit_count
    FROM article_edits
    ORDER BY edit_count DESC
    LIMIT 20
""").show(truncate=False)

print("\n========== TOP 20 MOST ACTIVE CONTRIBUTORS ==========")
spark.sql("""
    SELECT username, total_edits, total_reverts,
           ROUND(revert_ratio * 100, 2) AS revert_pct
    FROM contributors
    ORDER BY total_edits DESC
    LIMIT 20
""").show(truncate=False)

print("\n========== SUSPICIOUS ACCOUNTS (revert rate > 80%) ==========")
spark.sql("""
    SELECT username, total_edits, total_reverts,
           ROUND(revert_ratio * 100, 2) AS revert_pct
    FROM contributors
    WHERE revert_ratio > 0.80
    AND total_edits > 20
    ORDER BY revert_ratio DESC
    LIMIT 20
""").show(truncate=False)

print("\n========== EDIT COUNT DISTRIBUTION ==========")
spark.sql("""
    SELECT
        CASE
            WHEN edit_count BETWEEN 1 AND 10 THEN '1-10 edits'
            WHEN edit_count BETWEEN 11 AND 100 THEN '11-100 edits'
            WHEN edit_count BETWEEN 101 AND 1000 THEN '101-1000 edits'
            ELSE 'Over 1000 edits'
        END AS edit_bucket,
        COUNT(*) AS article_count
    FROM article_edits
    GROUP BY edit_bucket
    ORDER BY article_count DESC
""").show(truncate=False)

spark.stop()
print("\nDone.")
