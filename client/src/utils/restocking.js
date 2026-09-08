// Restocking allocation utility
// Mirrors the greedy fill in server/main.py::build_recommendations so dragging
// the budget slider re-ranks instantly instead of firing a request per pixel.
// The server stays authoritative: it recomputes the same allocation on submit.
//
// Candidates come from GET /api/restocking/recommendations at a budget large
// enough to fund everything, which is the only source that carries the
// server-derived lead_time_days alongside each shortfall.

export function buildRecommendations(candidates, budget) {
  const ranked = [...candidates].sort((a, b) => b.shortfall - a.shortfall)

  let remaining = Math.max(budget, 0)
  const recommendations = []

  for (const candidate of ranked) {
    // An item whose full shortfall does not fit is still bought down to
    // whatever whole units the remaining budget covers; a part-funded line is
    // a real answer, not an error. Zero-unit lines are dropped so the table
    // never renders an empty row.
    const affordable = Math.floor(remaining / candidate.unit_cost)
    const quantity = Math.min(candidate.shortfall, affordable)
    if (quantity <= 0) continue

    const lineTotal = round2(quantity * candidate.unit_cost)
    remaining = round2(remaining - lineTotal)
    recommendations.push({
      item_sku: candidate.item_sku,
      item_name: candidate.item_name,
      shortfall: candidate.shortfall,
      unit_cost: candidate.unit_cost,
      lead_time_days: candidate.lead_time_days,
      recommended_quantity: quantity,
      line_total: lineTotal,
      fully_funded: quantity === candidate.shortfall
    })
  }

  const totalCost = round2(recommendations.reduce((sum, r) => sum + r.line_total, 0))

  return {
    recommendations,
    totalCost,
    budgetRemaining: round2(Math.max(budget, 0) - totalCost),
    itemsRecommended: recommendations.length
  }
}

// Money maths in floats accumulates drift; every running total is snapped back
// to cents so the "remaining" figure cannot drift negative at the budget edge.
function round2(n) {
  return Math.round(n * 100) / 100
}
