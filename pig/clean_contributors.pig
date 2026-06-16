-- Load contributor stats from MapReduce output
raw_stats = LOAD '/wiki/output/contributor_stats/part-00000'
            USING PigStorage('\t')
            AS (contributor:chararray, edits:int, reverts:int);

-- Filter out bot accounts
no_bots = FILTER raw_stats BY NOT (contributor MATCHES '.*[Bb]ot.*');

-- Filter out anonymous IPs
registered = FILTER no_bots BY NOT (contributor MATCHES 'IP:.*');

-- Filter out low-activity accounts
active = FILTER registered BY edits >= 5;

-- Compute revert ratio
with_ratio = FOREACH active GENERATE
    contributor,
    edits,
    reverts,
    (float)reverts / (float)edits AS revert_ratio:float;

-- Sort by total edits descending
sorted = ORDER with_ratio BY edits DESC;

-- Store cleaned output back to HDFS
STORE sorted INTO '/wiki/processed/clean_contributors'
      USING PigStorage('\t');
