import csv
import json
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"
ANALYSIS = ROOT / "analysis"
random.seed(42)


FEEDS = [
    ("FEED001", "Enterprise AI Company Profiles", "company_profile", "Enterprise AI", "corp dev"),
    ("FEED002", "AI Infrastructure Deal Timeline", "deal_timeline", "AI Infrastructure", "investor"),
    ("FEED003", "Executive Move Watchlist", "executive_move", "Cloud Platforms", "consulting"),
    ("FEED004", "Private Market Funding Tracker", "funding_tracker", "Private Markets", "investor"),
    ("FEED005", "Cloud Vendor Sentiment Benchmark", "sentiment_benchmark", "Cloud Platforms", "enterprise"),
    ("FEED006", "Cybersecurity Buyer Intent Feed", "buyer_signal", "Cybersecurity", "enterprise"),
    ("FEED007", "Semiconductor Supply Chain Profiles", "company_profile", "Semiconductors", "advisory"),
    ("FEED008", "Fintech Partnership Timeline", "deal_timeline", "Fintech", "corp dev"),
    ("FEED009", "Creator Economy Company Index", "company_profile", "Creator Economy", "investor"),
    ("FEED010", "Private Capital Survey Benchmarks", "survey_benchmark", "Private Capital", "advisory"),
    ("FEED011", "M&A Advisory Signal Feed", "buyer_signal", "Dealmaking", "advisory"),
    ("FEED012", "Data Center Capacity Tracker", "funding_tracker", "AI Infrastructure", "enterprise"),
]

SOURCE_TYPES = [
    ("reported_story", 0.32),
    ("subscriber_survey", 0.18),
    ("reporter_note", 0.16),
    ("public_filing", 0.12),
    ("funding_database", 0.12),
    ("executive_briefing", 0.10),
]

SIGNAL_TYPES = [
    "funding_event",
    "executive_move",
    "product_launch",
    "customer_adoption",
    "vendor_spend",
    "partnership",
    "market_sentiment",
    "capacity_expansion",
    "valuation_marker",
    "go_to_market_shift",
]

SCHEMA_FIELDS = {
    "company_profile": [
        "company_name",
        "sector",
        "stage",
        "headcount_band",
        "funding_stage",
        "valuation_band",
        "proprietary_signal_count",
        "confidence_score",
    ],
    "deal_timeline": [
        "company_name",
        "event_date",
        "event_type",
        "counterparty",
        "deal_value_band",
        "source_count",
        "validation_status",
        "confidence_score",
    ],
    "executive_move": [
        "company_name",
        "executive_name",
        "role",
        "prior_company",
        "effective_date",
        "reporting_line",
        "source_count",
        "confidence_score",
    ],
    "funding_tracker": [
        "company_name",
        "round_type",
        "amount_band",
        "lead_investor",
        "valuation_band",
        "announcement_status",
        "source_count",
        "public_corroboration",
    ],
    "sentiment_benchmark": [
        "audience_segment",
        "sector",
        "question_theme",
        "sample_size",
        "positive_pct",
        "negative_pct",
        "trend_delta",
        "recurring_feed_fit",
    ],
    "buyer_signal": [
        "buyer_segment",
        "sector",
        "signal_theme",
        "signal_strength",
        "time_window",
        "sample_size",
        "confidence_score",
        "recommended_use",
    ],
    "survey_benchmark": [
        "audience_segment",
        "sector",
        "metric_name",
        "sample_size",
        "benchmark_value",
        "period",
        "trend_delta",
        "confidence_score",
    ],
}


def weighted_choice(options):
    total = sum(weight for _, weight in options)
    pick = random.random() * total
    running = 0
    for value, weight in options:
        running += weight
        if running >= pick:
            return value
    return options[-1][0]


def clamp(value, low, high):
    return max(low, min(high, value))


def rows_to_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def pct(value):
    return round(value * 100, 1)


def money_band():
    return random.choice(["<$25M", "$25M-$75M", "$75M-$250M", "$250M-$1B", ">$1B"])


def build_records():
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(exist_ok=True)

    source_documents = []
    companies = []
    extracted_signals = []
    taxonomy_terms = []
    survey_sentiment = []
    quality_checks = []

    sectors = sorted({feed[3] for feed in FEEDS})
    company_names = [
        "Atlas Vector",
        "Northstar Compute",
        "Cobalt Ledger",
        "SignalForge",
        "BrightLayer AI",
        "Nexus Cloud",
        "VaultSpan",
        "Meridian Chips",
        "CreatorGrid",
        "Harbor Robotics",
        "Prism Security",
        "CircuitLake",
        "FoundryStack",
        "Apex Data Centers",
        "LumenPay",
        "Orchid Systems",
        "VectorBridge",
        "Waypoint AI",
        "SageCompute",
        "Fathom Legal AI",
        "Copperline Fintech",
        "Kite Commerce",
        "Helio Semis",
        "Nimbus Agents",
        "Stride Cloud",
        "Forma Cyber",
        "ScaleMint",
        "PacketFoundry",
        "DriftWorks",
        "Beacon Infra",
        "TerraModel",
        "Pioneer GPU",
        "Mosaic Workflows",
        "ArcLight Data",
        "Tandem BioAI",
        "Vellum Apps",
    ]

    start = date(2026, 1, 5)
    for idx, name in enumerate(company_names, start=1):
        sector = random.choice(sectors)
        stage = random.choices(
            ["Seed", "Series A", "Series B", "Growth", "Pre IPO", "Public subsidiary"],
            weights=[6, 12, 24, 28, 20, 10],
        )[0]
        companies.append(
            {
                "company_id": f"CO{idx:03d}",
                "company_name": name,
                "sector": sector,
                "stage": stage,
                "hq_region": random.choice(["Bay Area", "New York", "Austin", "Seattle", "Boston", "London", "Singapore"]),
                "headcount_band": random.choice(["1-50", "51-200", "201-500", "501-1000", "1000+"]),
                "funding_stage": random.choice(["Bootstrapped", "Series A", "Series B", "Series C", "Growth", "Strategic backed"]),
                "valuation_band": money_band(),
                "profile_completeness": round(random.uniform(0.58, 0.97), 2),
                "public_corroboration_count": random.randint(0, 5),
                "proprietary_signal_count": random.randint(2, 15),
            }
        )

    for feed_id, feed_name, product_type, sector, buyer in FEEDS:
        docs_for_feed = random.randint(8, 14)
        for n in range(docs_for_feed):
            source_type = weighted_choice(SOURCE_TYPES)
            doc_id = f"DOC{len(source_documents) + 1:04d}"
            source_documents.append(
                {
                    "doc_id": doc_id,
                    "feed_id": feed_id,
                    "source_type": source_type,
                    "source_date": (start + timedelta(days=random.randint(0, 115))).isoformat(),
                    "sector": sector,
                    "reporting_desk": random.choice(["AI", "Finance", "Enterprise", "Semiconductors", "Consumer Tech"]),
                    "exclusivity_level": random.choice(["exclusive", "derived", "public corroboration", "survey only"]),
                    "buyer_relevance": random.randint(62, 98),
                    "extraction_complexity": random.randint(22, 88),
                    "access_tier": random.choice(["newsroom", "pro", "enterprise pilot"]),
                }
            )

        feed_docs = [row for row in source_documents if row["feed_id"] == feed_id]
        feed_companies = random.sample(companies, k=random.randint(8, 14))
        signal_count = random.randint(18, 32)
        for n in range(signal_count):
            doc = random.choice(feed_docs)
            company = random.choice(feed_companies)
            confidence = clamp(random.gauss(0.78, 0.12), 0.42, 0.98)
            validation = random.choices(
                ["validated", "needs public corroboration", "needs reporter review", "conflict found"],
                weights=[44, 28, 20, 8],
            )[0]
            value = random.randint(48, 96)
            if doc["exclusivity_level"] == "exclusive":
                value += 4
            if validation == "validated":
                value += 3
            value = min(99, value)
            fields = SCHEMA_FIELDS[product_type]
            filled = random.randint(max(4, len(fields) - 3), len(fields))
            extracted_signals.append(
                {
                    "signal_id": f"SIG{len(extracted_signals) + 1:04d}",
                    "feed_id": feed_id,
                    "doc_id": doc["doc_id"],
                    "company_id": company["company_id"],
                    "signal_type": random.choice(SIGNAL_TYPES),
                    "event_date": (start + timedelta(days=random.randint(0, 115))).isoformat(),
                    "buyer_use_case": buyer,
                    "target_product": product_type,
                    "schema_fields_required": len(fields),
                    "schema_fields_filled": filled,
                    "extraction_confidence": round(confidence, 2),
                    "source_count": random.randint(1, 5),
                    "validation_status": validation,
                    "commercial_value_score": value,
                    "launch_note": random.choice(
                        [
                            "ready for profile enrichment",
                            "map to controlled taxonomy",
                            "needs second source",
                            "candidate for recurring feed",
                            "hold for editorial context",
                        ]
                    ),
                }
            )

        if product_type in {"sentiment_benchmark", "buyer_signal", "survey_benchmark"} or random.random() > 0.42:
            for theme in random.sample(
                ["AI budget outlook", "vendor consolidation", "IPO appetite", "cloud spend", "security priorities", "M&A confidence"],
                k=3,
            ):
                positive = random.randint(34, 76)
                negative = random.randint(8, min(38, 92 - positive))
                neutral = 100 - positive - negative
                sample = random.randint(155, 720)
                survey_sentiment.append(
                    {
                        "survey_id": f"SUR{len(survey_sentiment) + 1:04d}",
                        "feed_id": feed_id,
                        "audience_segment": random.choice(["C suite", "investors", "operators", "advisors", "finance leaders"]),
                        "sector": sector,
                        "question_theme": theme,
                        "sample_size": sample,
                        "positive_pct": positive,
                        "neutral_pct": neutral,
                        "negative_pct": negative,
                        "trend_delta": random.randint(-14, 18),
                        "signal_strength": round((abs(positive - negative) / 100) * min(1, sample / 400), 2),
                        "recurring_feed_fit": random.choice(["high", "medium", "watch"]),
                    }
                )

        for dimension, terms in {
            "company_stage": ["Seed", "Series A", "Series B", "Growth", "Pre IPO"],
            "signal_type": SIGNAL_TYPES,
            "buyer_use_case": ["investor", "corp dev", "enterprise", "advisory", "consulting"],
            "validation_status": ["validated", "needs public corroboration", "needs reporter review", "conflict found"],
        }.items():
            for term in random.sample(terms, k=min(3, len(terms))):
                taxonomy_terms.append(
                    {
                        "taxonomy_id": f"TAX{len(taxonomy_terms) + 1:04d}",
                        "feed_id": feed_id,
                        "dimension": dimension,
                        "term": term,
                        "parent_term": "root" if dimension != "signal_type" else product_type,
                        "schema_field": dimension,
                        "buyer_use_case": buyer,
                        "owner": random.choice(["Data product", "Research operations", "Editorial liaison"]),
                        "governance_status": random.choices(["approved", "needs definition", "duplicate risk"], weights=[68, 24, 8])[0],
                    }
                )

    open_statuses = ["open", "in review", "resolved"]
    check_types = ["missing field", "taxonomy mismatch", "source conflict", "stale value", "low confidence", "buyer definition gap"]
    for signal in random.sample(extracted_signals, k=118):
        severity = random.choices(["critical", "high", "medium", "low"], weights=[8, 23, 44, 25])[0]
        quality_checks.append(
            {
                "check_id": f"QA{len(quality_checks) + 1:04d}",
                "feed_id": signal["feed_id"],
                "record_id": signal["signal_id"],
                "check_type": random.choice(check_types),
                "severity": severity,
                "status": random.choices(open_statuses, weights=[35, 28, 37])[0],
                "resolution_owner": random.choice(["Data analyst", "Reporter", "Product manager", "Research editor"]),
                "sla_hours": random.choice([12, 24, 48, 72]),
            }
        )

    return source_documents, companies, extracted_signals, taxonomy_terms, survey_sentiment, quality_checks


def score_feeds(source_documents, companies, extracted_signals, taxonomy_terms, survey_sentiment, quality_checks):
    docs_by_feed = defaultdict(list)
    signals_by_feed = defaultdict(list)
    taxonomy_by_feed = defaultdict(list)
    surveys_by_feed = defaultdict(list)
    qa_by_feed = defaultdict(list)

    for row in source_documents:
        docs_by_feed[row["feed_id"]].append(row)
    for row in extracted_signals:
        signals_by_feed[row["feed_id"]].append(row)
    for row in taxonomy_terms:
        taxonomy_by_feed[row["feed_id"]].append(row)
    for row in survey_sentiment:
        surveys_by_feed[row["feed_id"]].append(row)
    for row in quality_checks:
        qa_by_feed[row["feed_id"]].append(row)

    queue = []
    for feed_id, feed_name, product_type, sector, buyer in FEEDS:
        docs = docs_by_feed[feed_id]
        signals = signals_by_feed[feed_id]
        taxonomy = taxonomy_by_feed[feed_id]
        surveys = surveys_by_feed[feed_id]
        qa = qa_by_feed[feed_id]

        avg_commercial = sum(int(s["commercial_value_score"]) for s in signals) / len(signals)
        avg_confidence = sum(float(s["extraction_confidence"]) for s in signals) / len(signals)
        avg_schema = sum(int(s["schema_fields_filled"]) / int(s["schema_fields_required"]) for s in signals) / len(signals)
        validated = sum(1 for s in signals if s["validation_status"] == "validated")
        validation_coverage = validated / len(signals)
        approved_taxonomy = sum(1 for t in taxonomy if t["governance_status"] == "approved") / len(taxonomy)
        survey_strength = sum(float(s["signal_strength"]) for s in surveys) / len(surveys) if surveys else 0.34
        open_high = sum(1 for q in qa if q["status"] != "resolved" and q["severity"] in {"critical", "high"})
        qa_risk = min(1, open_high / 8)
        source_depth = min(1, len(docs) / 12)

        readiness = (
            0.22 * (avg_commercial / 100)
            + 0.18 * avg_schema
            + 0.16 * avg_confidence
            + 0.15 * validation_coverage
            + 0.12 * approved_taxonomy
            + 0.10 * survey_strength
            + 0.07 * source_depth
            - 0.12 * qa_risk
        )
        readiness_score = round(clamp(readiness / 0.82, 0, 1) * 100, 1)

        if readiness_score >= 82 and open_high <= 2:
            lane = "launch pilot"
        elif readiness_score >= 72:
            lane = "clean and package"
        elif readiness_score >= 62:
            lane = "enrich before selling"
        else:
            lane = "hold for rebuild"

        queue.append(
            {
                "feed_id": feed_id,
                "feed_name": feed_name,
                "target_product": product_type,
                "sector": sector,
                "primary_buyer": buyer,
                "source_documents": len(docs),
                "extracted_signals": len(signals),
                "avg_commercial_value": round(avg_commercial, 1),
                "schema_readiness_pct": pct(avg_schema),
                "extraction_confidence_pct": pct(avg_confidence),
                "validation_coverage_pct": pct(validation_coverage),
                "taxonomy_approved_pct": pct(approved_taxonomy),
                "survey_strength_pct": pct(survey_strength),
                "open_high_risk_qa": open_high,
                "readiness_score": readiness_score,
                "launch_lane": lane,
                "recommended_next_step": next_step(lane),
            }
        )

    queue.sort(key=lambda row: float(row["readiness_score"]), reverse=True)
    return queue


def next_step(lane):
    if lane == "launch pilot":
        return "Package sample file, buyer brief, and recurring refresh SLA."
    if lane == "clean and package":
        return "Close high-severity QA and lock required fields."
    if lane == "enrich before selling":
        return "Add public corroboration and resolve taxonomy gaps."
    return "Redesign schema before commercial review."


def build_outputs(records):
    source_documents, companies, extracted_signals, taxonomy_terms, survey_sentiment, quality_checks = records
    feed_queue = score_feeds(source_documents, companies, extracted_signals, taxonomy_terms, survey_sentiment, quality_checks)

    signal_lookup = {row["signal_id"]: row for row in extracted_signals}
    company_lookup = {row["company_id"]: row for row in companies}
    feed_lookup = {row[0]: row for row in FEEDS}

    extraction_queue = []
    for signal in extracted_signals:
        company = company_lookup[signal["company_id"]]
        validation_penalty = {
            "validated": 0,
            "needs public corroboration": 10,
            "needs reporter review": 14,
            "conflict found": 24,
        }[signal["validation_status"]]
        missing_fields = int(signal["schema_fields_required"]) - int(signal["schema_fields_filled"])
        priority = (
            int(signal["commercial_value_score"])
            + missing_fields * 4
            + validation_penalty
            + (1 - float(signal["extraction_confidence"])) * 22
        )
        extraction_queue.append(
            {
                "signal_id": signal["signal_id"],
                "feed_id": signal["feed_id"],
                "feed_name": feed_lookup[signal["feed_id"]][1],
                "company_name": company["company_name"],
                "sector": company["sector"],
                "signal_type": signal["signal_type"],
                "buyer_use_case": signal["buyer_use_case"],
                "validation_status": signal["validation_status"],
                "schema_fields_filled": signal["schema_fields_filled"],
                "schema_fields_required": signal["schema_fields_required"],
                "extraction_confidence_pct": pct(float(signal["extraction_confidence"])),
                "commercial_value_score": signal["commercial_value_score"],
                "triage_priority": round(priority, 1),
                "next_action": signal["launch_note"],
            }
        )
    extraction_queue.sort(key=lambda row: float(row["triage_priority"]), reverse=True)

    schema_queue = []
    taxonomy_by_feed = defaultdict(list)
    for row in taxonomy_terms:
        taxonomy_by_feed[row["feed_id"]].append(row)
    for feed_id, feed_name, product_type, sector, buyer in FEEDS:
        fields = SCHEMA_FIELDS[product_type]
        terms = taxonomy_by_feed[feed_id]
        approved = sum(1 for row in terms if row["governance_status"] == "approved")
        definition_gaps = sum(1 for row in terms if row["governance_status"] != "approved")
        field_coverage = round(random.uniform(0.68, 0.96), 2)
        schema_queue.append(
            {
                "feed_id": feed_id,
                "feed_name": feed_name,
                "target_product": product_type,
                "required_fields": len(fields),
                "field_coverage_pct": pct(field_coverage),
                "taxonomy_terms": len(terms),
                "approved_terms": approved,
                "definition_gaps": definition_gaps,
                "schema_owner": random.choice(["Data product", "Research operations", "Editorial liaison"]),
                "governance_lane": "certify" if definition_gaps <= 2 and field_coverage >= 0.84 else "repair",
            }
        )

    client_brief = []
    for row in feed_queue[:6]:
        client_brief.append(
            {
                "feed_name": row["feed_name"],
                "primary_buyer": row["primary_buyer"],
                "readiness_score": row["readiness_score"],
                "launch_lane": row["launch_lane"],
                "buyer_value": buyer_value(row["primary_buyer"], row["target_product"]),
                "proof_points": f"{row['source_documents']} source docs, {row['extracted_signals']} extracted signals, {row['validation_coverage_pct']}% validation coverage",
                "blocker": blocker(row),
                "recommendation": row["recommended_next_step"],
            }
        )

    summary = {
        "feeds": len(FEEDS),
        "source_documents": len(source_documents),
        "companies": len(companies),
        "extracted_signals": len(extracted_signals),
        "taxonomy_terms": len(taxonomy_terms),
        "survey_records": len(survey_sentiment),
        "quality_checks": len(quality_checks),
        "launch_pilot_feeds": sum(1 for row in feed_queue if row["launch_lane"] == "launch pilot"),
        "clean_package_feeds": sum(1 for row in feed_queue if row["launch_lane"] == "clean and package"),
        "top_feed": feed_queue[0]["feed_name"],
        "top_score": feed_queue[0]["readiness_score"],
        "avg_readiness_score": round(sum(float(row["readiness_score"]) for row in feed_queue) / len(feed_queue), 1),
        "open_high_risk_qa": sum(int(row["open_high_risk_qa"]) for row in feed_queue),
    }

    payload = {
        "summary": summary,
        "feedQueue": feed_queue,
        "extractionQueue": extraction_queue[:40],
        "schemaQueue": schema_queue,
        "clientBrief": client_brief,
        "surveySentiment": survey_sentiment,
        "qualityChecks": quality_checks,
    }

    return feed_queue, extraction_queue, schema_queue, client_brief, summary, payload


def buyer_value(buyer, product_type):
    values = {
        "investor": "Prioritize private-market diligence targets before the signal is broadly visible.",
        "corp dev": "Spot acquisition, partnership, and competitive shifts from structured reporting signals.",
        "enterprise": "Benchmark vendor, budget, and adoption signals against peer decision makers.",
        "advisory": "Package sector narratives into repeatable client-ready evidence.",
        "consulting": "Translate executive moves and operating changes into account planning context.",
    }
    if product_type == "sentiment_benchmark":
        return "Track decision-maker sentiment as a recurring market barometer."
    return values[buyer]


def blocker(row):
    if int(row["open_high_risk_qa"]) > 3:
        return "Open high-risk QA checks need owner resolution."
    if float(row["schema_readiness_pct"]) < 82:
        return "Required fields need stronger completion before recurring delivery."
    if float(row["validation_coverage_pct"]) < 50:
        return "Validation coverage needs public or second-source support."
    return "No launch blocker beyond final packaging."


def write_docs(summary, feed_queue, extraction_queue):
    top = feed_queue[0]
    findings = f"""# Executive Findings

## What I Analyzed

I modeled a proprietary intelligence product workflow with {summary['source_documents']} synthetic source documents, {summary['companies']} company profiles, {summary['extracted_signals']} extracted signals, {summary['taxonomy_terms']} taxonomy terms, {summary['survey_records']} survey records, and {summary['quality_checks']} quality checks.

## Findings

- The strongest launch candidate is {top['feed_name']} with a readiness score of {top['readiness_score']}.
- {summary['launch_pilot_feeds']} feeds are ready for pilot packaging, while {summary['clean_package_feeds']} need cleanup before enterprise delivery.
- The queue exposes {summary['open_high_risk_qa']} open high-risk QA items, which is the main constraint on recurring feed reliability.
- The top extraction queue is driven by commercial value, missing schema fields, validation gaps, and extraction confidence.

## Recommendation

Launch the highest-scoring feed as a controlled enterprise pilot, close high-risk QA before recurring delivery, and use the taxonomy queue to keep editorial signals reusable across profiles, timelines, sentiment benchmarks, and buyer briefings.
"""

    plan = """# Analysis Plan

1. Generate synthetic newsroom-style source documents across reporting, surveys, notes, filings, funding databases, and executive briefings.
2. Extract company, deal, executive, sentiment, and buyer-intent signals into required product schemas.
3. Score each signal by commercial value, extraction confidence, schema completion, and validation status.
4. Score each feed by buyer fit, schema readiness, validation coverage, taxonomy governance, survey strength, source depth, and QA risk.
5. Produce four outputs: launch queue, extraction and enrichment queue, schema governance queue, and enterprise buyer brief.
"""

    sql = """-- Feed launch readiness by buyer and product type
select
  target_product,
  primary_buyer,
  count(*) as feeds,
  avg(readiness_score) as avg_readiness_score,
  sum(open_high_risk_qa) as open_high_risk_qa
from feed_launch_queue
group by target_product, primary_buyer
order by avg_readiness_score desc;

-- Extraction records needing analyst validation before packaging
select
  feed_name,
  company_name,
  signal_type,
  validation_status,
  extraction_confidence_pct,
  triage_priority
from extraction_enrichment_queue
where validation_status <> 'validated'
order by triage_priority desc;

-- Taxonomy gaps by feed
select
  feed_name,
  required_fields,
  field_coverage_pct,
  taxonomy_terms,
  definition_gaps,
  governance_lane
from schema_governance_queue
where governance_lane = 'repair'
order by definition_gaps desc, field_coverage_pct asc;
"""

    data_readme = """# Data Sources

All data in this folder is synthetic and generated by `scripts/score_operating_data.py` with a fixed random seed.

The structure is modeled on subscription intelligence product work where analysts convert editorial reporting, survey responses, org-chart updates, funding signals, executive moves, public filings, and private-market research into reusable enterprise data feeds.

- `source_documents.csv`: Source-level metadata for reported stories, surveys, reporter notes, filings, funding databases, and briefings.
- `company_profiles.csv`: Synthetic private-company profile records with stage, sector, headcount band, valuation band, and corroboration counts.
- `extracted_signals.csv`: Record-level extracted facts mapped to target product schemas.
- `taxonomy_terms.csv`: Controlled vocabulary and governance status for productized intelligence fields.
- `survey_sentiment.csv`: Synthetic recurring survey signals by audience segment, sector, and question theme.
- `quality_checks.csv`: Validation, taxonomy, confidence, and source conflict checks.
"""

    data_dictionary = """# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `source_documents.csv` | source document | Tracks source type, desk, exclusivity level, buyer relevance, and extraction complexity. |
| `company_profiles.csv` | company | Holds synthetic private-company profile attributes used for enrichment. |
| `extracted_signals.csv` | extracted signal | Maps raw intelligence signals to target product schemas with confidence and validation status. |
| `taxonomy_terms.csv` | taxonomy term | Shows controlled vocabulary ownership, schema field mapping, and governance status. |
| `survey_sentiment.csv` | survey cut | Captures recurring sentiment benchmarks by audience, sector, and question theme. |
| `quality_checks.csv` | QA check | Captures field gaps, source conflicts, taxonomy mismatches, and owner SLAs. |
| `analysis/outputs/feed_launch_queue.csv` | feed | Ranked recurring data feed readiness queue. |
| `analysis/outputs/extraction_enrichment_queue.csv` | signal | Analyst queue for validation, enrichment, and schema completion. |
| `analysis/outputs/schema_governance_queue.csv` | feed schema | Schema and taxonomy readiness by target product. |
| `analysis/outputs/client_brief.csv` | feed | Buyer-facing launch rationale, proof points, blockers, and recommendation. |
"""

    status = f"""# Status

- Status: upgraded through the Portfolio Artifact Upgrade Workflow
- Artifact type: proprietary intelligence data product schema and feed readiness workbench
- Generated records: {summary['source_documents']} source documents, {summary['extracted_signals']} extracted signals, {summary['taxonomy_terms']} taxonomy terms, {summary['quality_checks']} QA checks
- Top launch candidate: {top['feed_name']} at readiness score {top['readiness_score']}

## Completed

- Rebuilt synthetic data around editorial intelligence productization, not generic dashboard metrics.
- Added transparent readiness scoring for recurring enterprise feed launch decisions.
- Added four distinct browser surfaces: launch cockpit, extraction queue, schema governance, and buyer brief.
- Rewrote analysis outputs, SQL examples, data documentation, and README for interview discussion.
"""

    (ANALYSIS / "executive_findings.md").write_text(findings)
    (ANALYSIS / "analysis_plan.md").write_text(plan)
    (ANALYSIS / "sql_checks.sql").write_text(sql)
    (DATA / "README.md").write_text(data_readme)
    (ROOT / "data_dictionary.md").write_text(data_dictionary)
    (ROOT / "STATUS.md").write_text(status)


def main():
    records = build_records()
    source_documents, companies, extracted_signals, taxonomy_terms, survey_sentiment, quality_checks = records
    feed_queue, extraction_queue, schema_queue, client_brief, summary, payload = build_outputs(records)

    rows_to_csv(DATA / "source_documents.csv", source_documents, list(source_documents[0].keys()))
    rows_to_csv(DATA / "company_profiles.csv", companies, list(companies[0].keys()))
    rows_to_csv(DATA / "extracted_signals.csv", extracted_signals, list(extracted_signals[0].keys()))
    rows_to_csv(DATA / "taxonomy_terms.csv", taxonomy_terms, list(taxonomy_terms[0].keys()))
    rows_to_csv(DATA / "survey_sentiment.csv", survey_sentiment, list(survey_sentiment[0].keys()))
    rows_to_csv(DATA / "quality_checks.csv", quality_checks, list(quality_checks[0].keys()))

    rows_to_csv(OUTPUTS / "feed_launch_queue.csv", feed_queue, list(feed_queue[0].keys()))
    rows_to_csv(OUTPUTS / "extraction_enrichment_queue.csv", extraction_queue, list(extraction_queue[0].keys()))
    rows_to_csv(OUTPUTS / "schema_governance_queue.csv", schema_queue, list(schema_queue[0].keys()))
    rows_to_csv(OUTPUTS / "client_brief.csv", client_brief, list(client_brief[0].keys()))
    (OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUTPUTS / "app_payload.json").write_text(json.dumps(payload, indent=2))

    write_docs(summary, feed_queue, extraction_queue)

    print(f"Generated {summary['extracted_signals']} extracted signals across {summary['feeds']} feeds.")
    print(f"Top launch candidate: {summary['top_feed']} ({summary['top_score']}).")


if __name__ == "__main__":
    main()
