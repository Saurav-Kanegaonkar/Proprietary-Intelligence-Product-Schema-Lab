-- Feed launch readiness by buyer and product type
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
