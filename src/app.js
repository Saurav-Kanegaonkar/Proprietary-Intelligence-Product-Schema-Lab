const payloadUrl = "analysis/outputs/app_payload.json";

const weights = [
  ["Commercial value", 22, "Buyer demand and differentiated signal value"],
  ["Schema readiness", 18, "Required fields filled for repeatable delivery"],
  ["Extraction confidence", 16, "How reliable the structured signal is"],
  ["Validation coverage", 15, "Second-source and public corroboration strength"],
  ["Taxonomy governance", 12, "Controlled vocabulary approval"],
  ["Survey strength", 10, "Useful recurring audience signal"],
  ["Source depth", 7, "Reporting and evidence volume"],
  ["QA risk", -12, "Open high-risk checks reduce readiness"],
];

function text(selector, value) {
  document.querySelector(selector).textContent = value;
}

function pct(value) {
  return `${Number(value).toFixed(1)}%`;
}

function scoreClass(score) {
  if (score >= 82) return "good";
  if (score >= 72) return "watch";
  return "risk";
}

function laneClass(lane) {
  if (lane === "launch pilot") return "good";
  if (lane === "clean and package") return "watch";
  return "risk";
}

function productLabel(value) {
  return value.replaceAll("_", " ");
}

function renderSummary(summary) {
  text('[data-field="topFeed"]', summary.top_feed);
  text('[data-field="topScore"]', summary.top_score);

  const metrics = [
    ["Feeds modeled", summary.feeds, "recurring product candidates"],
    ["Extracted signals", summary.extracted_signals, "structured intelligence records"],
    ["Avg readiness", `${summary.avg_readiness_score}/100`, "portfolio score"],
    ["Open high-risk QA", summary.open_high_risk_qa, "must close before scale"],
  ];

  document.querySelector("#summaryMetrics").innerHTML = metrics
    .map(([label, value, note]) => `
      <article class="metric-card">
        <span>${label}</span>
        <strong>${value}</strong>
        <em>${note}</em>
      </article>
    `)
    .join("");
}

function renderFeedQueue(rows) {
  document.querySelector("#feedRows").innerHTML = rows
    .map((row) => `
      <tr>
        <td>
          <strong>${row.feed_name}</strong>
          <span>${productLabel(row.target_product)} · ${row.sector}</span>
        </td>
        <td>${row.primary_buyer}</td>
        <td><b class="score ${scoreClass(Number(row.readiness_score))}">${row.readiness_score}</b></td>
        <td>${pct(row.schema_readiness_pct)}</td>
        <td>${pct(row.validation_coverage_pct)}</td>
        <td><span class="pill ${laneClass(row.launch_lane)}">${row.launch_lane}</span></td>
      </tr>
    `)
    .join("");
}

function renderWeights() {
  document.querySelector("#weightList").innerHTML = weights
    .map(([label, weight, note]) => `
      <article>
        <div>
          <strong>${label}</strong>
          <span>${note}</span>
        </div>
        <b>${weight > 0 ? "+" : ""}${weight}%</b>
      </article>
    `)
    .join("");
}

function renderExtraction(rows) {
  document.querySelector("#signalCards").innerHTML = rows
    .slice(0, 10)
    .map((row) => `
      <article class="record-card">
        <div>
          <span class="pill ${row.validation_status === "validated" ? "good" : "watch"}">${row.validation_status}</span>
          <strong>${row.company_name}</strong>
          <em>${row.feed_name}</em>
        </div>
        <dl>
          <div><dt>Signal</dt><dd>${productLabel(row.signal_type)}</dd></div>
          <div><dt>Confidence</dt><dd>${pct(row.extraction_confidence_pct)}</dd></div>
          <div><dt>Fields</dt><dd>${row.schema_fields_filled}/${row.schema_fields_required}</dd></div>
          <div><dt>Priority</dt><dd>${row.triage_priority}</dd></div>
        </dl>
        <p>${row.next_action}</p>
      </article>
    `)
    .join("");

  const counts = rows.reduce((acc, row) => {
    acc[row.validation_status] = (acc[row.validation_status] || 0) + 1;
    return acc;
  }, {});
  const total = rows.length;
  document.querySelector("#validationStack").innerHTML = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([label, count]) => {
      const width = Math.round((count / total) * 100);
      return `
        <article>
          <div><strong>${label}</strong><span>${count} records</span></div>
          <div class="bar"><i style="width:${width}%"></i></div>
        </article>
      `;
    })
    .join("");
}

function renderSchema(rows, checks) {
  document.querySelector("#schemaRows").innerHTML = rows
    .map((row) => `
      <tr>
        <td><strong>${row.feed_name}</strong></td>
        <td>${productLabel(row.target_product)}</td>
        <td>${row.required_fields}</td>
        <td>${pct(row.field_coverage_pct)}</td>
        <td>${row.approved_terms}/${row.taxonomy_terms}</td>
        <td><span class="pill ${row.governance_lane === "certify" ? "good" : "watch"}">${row.governance_lane}</span></td>
      </tr>
    `)
    .join("");

  document.querySelector("#qaList").innerHTML = checks
    .filter((row) => row.status !== "resolved")
    .slice(0, 9)
    .map((row) => `
      <article>
        <span class="severity ${row.severity}">${row.severity}</span>
        <strong>${row.check_type}</strong>
        <em>${row.resolution_owner} · ${row.sla_hours}h SLA</em>
      </article>
    `)
    .join("");
}

function renderBrief(rows) {
  document.querySelector("#briefCards").innerHTML = rows
    .map((row) => `
      <article class="brief-card">
        <span class="pill ${laneClass(row.launch_lane)}">${row.launch_lane}</span>
        <h3>${row.feed_name}</h3>
        <dl>
          <div><dt>Buyer</dt><dd>${row.primary_buyer}</dd></div>
          <div><dt>Readiness</dt><dd>${row.readiness_score}/100</dd></div>
        </dl>
        <p>${row.buyer_value}</p>
        <b>${row.proof_points}</b>
        <em>${row.blocker}</em>
        <strong>${row.recommendation}</strong>
      </article>
    `)
    .join("");
}

function wireTabs() {
  const buttons = document.querySelectorAll("[data-view]");
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      buttons.forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".surface").forEach((surface) => surface.classList.remove("active"));
      button.classList.add("active");
      document.querySelector(`#${button.dataset.view}`).classList.add("active");
    });
  });
}

async function init() {
  const response = await fetch(payloadUrl);
  const data = await response.json();
  renderSummary(data.summary);
  renderFeedQueue(data.feedQueue);
  renderWeights();
  renderExtraction(data.extractionQueue);
  renderSchema(data.schemaQueue, data.qualityChecks);
  renderBrief(data.clientBrief);
  wireTabs();
}

init();
