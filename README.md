# Wikipedia Edit Analytics and Vandalism Detection System

A Big Data Analytics pipeline that processes Wikipedia's full edit history to identify contested articles, profile contributors, and detect coordinated vandalism — built using a Lambda Architecture on a local Hadoop cluster.

---

## Project Overview

Wikipedia is one of the largest collaboratively edited knowledge bases in the world. This project analyzes millions of edits from Wikipedia's public edit history dump to answer key questions:

- Which articles are the most contested and frequently edited?
- Who are the most active contributors, and how many of their edits are reverts?
- Can we detect suspicious accounts or coordinated vandalism patterns?
- How do articles distribute across contention tiers?

---

## Architecture — Lambda Architecture

```
Raw Wikipedia XML Dump (3.8 GB)
            |
            v
    [ HDFS — Raw Storage ]
            |
     ---------------
     |             |
     v             v
 Batch Layer    Speed Layer
 (MapReduce)   (Spark RDD)
     |             |
     v             v
 Apache Pig    Spark SQL
 (Cleaning)    (Queries)
     |             |
     ---------------
            |
            v
    [ Serving Layer ]
     HBase Simulation
            |
            v
     HTML Dashboard
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Cluster | Hadoop 3.3.6 (Pseudo-distributed, WSL2) |
| Batch Processing | MapReduce (Python Streaming) |
| Data Cleaning | Apache Pig 0.17.0 |
| Analytical Queries | Apache Spark 3.5.1 (Spark SQL) |
| Contention Detection | Apache Spark 3.5.1 (RDD API) |
| Serving Layer | HBase 2.5.7 (Python simulation) |
| Visualization | Local HTML Dashboard |
| Language | Python, PigLatin |
| OS | Ubuntu 22.04 on WSL2 |

> **Note:** Hive 3.1.3 was evaluated but abandoned due to a ClassCastException JVM compatibility bug. Replaced with Spark SQL. HBase real installation was replaced with a Python simulation due to Zookeeper port binding issues under WSL2.

---

## Dataset

**Source:** Wikipedia Edit History Dump (English)
**File:** `enwiki-latest-stub-meta-history1.xml.gz`
**Size:** 3.8 GB compressed
**Download:** [https://dumps.wikimedia.org/enwiki/latest/](https://dumps.wikimedia.org/enwiki/latest/)

The dataset is not included in this repository due to file size. Download the stub meta history dump and place it in `raw_data/` before running.

---

## Pipeline Components

### 1. MapReduce Job 1 — Edit Count per Article
Counts the total number of edits for every article across the entire dataset.

**Top Results:**
| Article | Edit Count |
|---|---|
| Wikipedia:Reference desk/Miscellaneous | 350,400 |
| Talk:Intelligent design | 33,151 |
| Talk:Israel | 30,088 |
| India | 29,381 |
| United Kingdom | 28,672 |
| World War II | 28,283 |
| Britney Spears | 27,786 |

### 2. MapReduce Job 2 — Contributor Profiling
Profiles every contributor by counting their total edits and revert count.

**Top Contributors:**
| Username | Total Edits | Reverts |
|---|---|---|
| ClueBot NG | 347,977 | 347,870 |
| Citation bot | 155,349 | 4 |
| ClueBot | 125,210 | 125,206 |
| AnomieBOT | 118,588 | 128 |
| InternetArchiveBot | 105,184 | 0 |

### 3. Apache Pig — Data Cleaning
Filters out known bots and computes revert ratios for all remaining human contributors.

**Suspicious Accounts (High Revert Ratio):**
| Username | Total Edits | Reverts | Revert Ratio |
|---|---|---|---|
| J.delanoy | 26,265 | 25,570 | 97.35% |
| Favonian | 34,225 | 30,417 | 88.87% |
| Materialscientist | 83,408 | 67,957 | 81.48% |

### 4. Spark SQL — Analytical Queries
Four SQL queries run against the processed data:
- Top 20 most edited articles
- Top 20 most active contributors with revert percentages
- Suspicious accounts (revert rate > 80%)
- Edit count distribution across buckets

**Edit Count Distribution:**
| Bucket | Article Count |
|---|---|
| 101–1,000 edits | 12,046 |
| Over 1,000 edits | 9,848 |
| 11–100 edits | 4,509 |
| 1–10 edits | 4,362 |

### 5. Spark RDD — Contention Tier Analysis
Classifies all 30,765 articles into contention tiers based on edit count.

| Tier | Threshold | Article Count |
|---|---|---|
| Extreme contention | > 10,000 edits | 463 |
| High contention | 5,000–10,000 edits | 1,653 |
| Medium contention | 1,000–5,000 edits | 7,732 |
| Low contention | < 1,000 edits | 20,917 |

### 6. HBase Serving Layer (Simulated)
Demonstrates PUT, GET, and SCAN operations on a `wiki_contention` table using a Python simulation of HBase's column-family data model.

---

## Project Structure

```
wiki_project/
├── mapreduce/
│   ├── edit_count_mapper.py
│   ├── edit_count_reducer.py
│   ├── contributor_mapper.py
│   └── contributor_reducer.py
├── pig/
│   └── clean_contributors.pig
├── spark/
│   ├── wiki_analysis.py        # Spark SQL queries
│   └── edit_storm_detector.py  # Spark RDD contention tiers
├── hbase/
│   └── hbase_simulation.py
└── .gitignore
```

---

## How to Run

### Prerequisites
- WSL2 Ubuntu 22.04
- Java 11
- Hadoop 3.3.6
- Apache Pig 0.17.0
- Apache Spark 3.5.1
- Python 3

### Startup
```bash
sudo service ssh start
start-dfs.sh
start-yarn.sh
jps   # verify all daemons are running
```

### Load Data into HDFS
```bash
hdfs dfs -mkdir -p /wiki/raw
hdfs dfs -put raw_data/enwiki-latest-stub-meta-history1.xml.gz /wiki/raw/
```

### Run MapReduce Jobs
```bash
# Job 1 — Edit counts
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input /wiki/raw/ -output /wiki/output/edit_counts \
  -mapper mapreduce/edit_count_mapper.py \
  -reducer mapreduce/edit_count_reducer.py

# Job 2 — Contributor profiling
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input /wiki/raw/ -output /wiki/output/contributor_stats \
  -mapper mapreduce/contributor_mapper.py \
  -reducer mapreduce/contributor_reducer.py
```

### Run Pig Cleaning
```bash
pig -f pig/clean_contributors.pig
```

### Run Spark Analysis
```bash
spark-submit spark/wiki_analysis.py
spark-submit spark/edit_storm_detector.py
```

### Run HBase Simulation
```bash
python3 hbase/hbase_simulation.py
```

---

## Key Findings

- **463 articles** fall in the extreme contention tier (>10,000 edits), indicating persistent editorial conflict
- **ClueBot NG** made 347,977 edits — nearly all reverts — confirming it as the primary anti-vandalism bot on Wikipedia
- **J.delanoy** had a 97.35% revert rate across 26,265 edits, flagging coordinated or repetitive editing behavior
- Topics like **Israel, Intelligent Design, Homeopathy, and Race and intelligence** appear in the top contested articles — consistent with known Wikipedia edit-war patterns
- The edit distribution is heavily skewed — most articles have fewer than 100 edits, while a small number attract tens of thousands

---

## Author

**Vedashri** — 
