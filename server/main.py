from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import statistics
from mock_data import inventory_items, orders, demand_forecasts, backlog_items, spending_summary, monthly_spending, category_spending, recent_transactions, purchase_orders

app = FastAPI(title="Factory Inventory Management System")

# Quarter mapping for date filtering
QUARTER_MAP = {
    'Q1-2025': ['2025-01', '2025-02', '2025-03'],
    'Q2-2025': ['2025-04', '2025-05', '2025-06'],
    'Q3-2025': ['2025-07', '2025-08', '2025-09'],
    'Q4-2025': ['2025-10', '2025-11', '2025-12']
}

def filter_by_month(items: list, month: Optional[str]) -> list:
    """Filter items by month/quarter based on order_date field"""
    if not month or month == 'all':
        return items

    if month.startswith('Q'):
        # Handle quarters
        if month in QUARTER_MAP:
            months = QUARTER_MAP[month]
            return [item for item in items if any(m in item.get('order_date', '') for m in months)]
    else:
        # Direct month match
        return [item for item in items if month in item.get('order_date', '')]

    return items

def apply_filters(items: list, warehouse: Optional[str] = None, category: Optional[str] = None,
                 status: Optional[str] = None) -> list:
    """Apply common filters to a list of items"""
    filtered = items

    if warehouse and warehouse != 'all':
        filtered = [item for item in filtered if item.get('warehouse') == warehouse]

    if category and category != 'all':
        filtered = [item for item in filtered if item.get('category', '').lower() == category.lower()]

    if status and status != 'all':
        filtered = [item for item in filtered if item.get('status', '').lower() == status.lower()]

    return filtered

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class InventoryItem(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    warehouse: str
    quantity_on_hand: int
    reorder_point: int
    unit_cost: float
    location: str
    last_updated: str

class Order(BaseModel):
    id: str
    order_number: str
    customer: str
    items: List[dict]
    status: str
    order_date: str
    expected_delivery: str
    total_value: float
    actual_delivery: Optional[str] = None
    warehouse: Optional[str] = None
    category: Optional[str] = None
    # Set only on orders created by the Restocking tab; lets the Orders view
    # split them into their own section without a second request.
    is_restock: Optional[bool] = False
    lead_time_days: Optional[int] = None

class DemandForecast(BaseModel):
    id: str
    item_sku: str
    item_name: str
    current_demand: int
    forecasted_demand: int
    trend: str
    period: str
    unit_cost: float

class BacklogItem(BaseModel):
    id: str
    order_id: str
    item_sku: str
    item_name: str
    quantity_needed: int
    quantity_available: int
    days_delayed: int
    priority: str
    has_purchase_order: Optional[bool] = False

class PurchaseOrder(BaseModel):
    id: str
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    status: str
    created_date: str
    notes: Optional[str] = None

class CreatePurchaseOrderRequest(BaseModel):
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    notes: Optional[str] = None

# API endpoints
@app.get("/")
def root():
    return {"message": "Factory Inventory Management System API", "version": "1.0.0"}

@app.get("/api/inventory", response_model=List[InventoryItem])
def get_inventory(
    warehouse: Optional[str] = None,
    category: Optional[str] = None
):
    """Get all inventory items with optional filtering"""
    return apply_filters(inventory_items, warehouse, category)

@app.get("/api/inventory/{item_id}", response_model=InventoryItem)
def get_inventory_item(item_id: str):
    """Get a specific inventory item"""
    item = next((item for item in inventory_items if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/api/orders", response_model=List[Order])
def get_orders(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get all orders with optional filtering"""
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)
    return filtered_orders

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    """Get a specific order"""
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/demand", response_model=List[DemandForecast])
def get_demand_forecasts():
    """Get demand forecasts"""
    return demand_forecasts

@app.get("/api/backlog", response_model=List[BacklogItem])
def get_backlog():
    """Get backlog items with purchase order status"""
    # Add has_purchase_order flag to each backlog item
    result = []
    for item in backlog_items:
        item_dict = dict(item)
        # Check if this backlog item has a purchase order
        has_po = any(po["backlog_item_id"] == item["id"] for po in purchase_orders)
        item_dict["has_purchase_order"] = has_po
        result.append(item_dict)
    return result

@app.get("/api/dashboard/summary")
def get_dashboard_summary(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get summary statistics for dashboard with optional filtering"""
    # Filter inventory
    filtered_inventory = apply_filters(inventory_items, warehouse, category)

    # Filter orders
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)

    total_inventory_value = sum(item["quantity_on_hand"] * item["unit_cost"] for item in filtered_inventory)
    low_stock_items = len([item for item in filtered_inventory if item["quantity_on_hand"] <= item["reorder_point"]])
    pending_orders = len([order for order in filtered_orders if order["status"] in ["Processing", "Backordered"]])
    total_backlog_items = len(backlog_items)

    return {
        "total_inventory_value": round(total_inventory_value, 2),
        "low_stock_items": low_stock_items,
        "pending_orders": pending_orders,
        "total_backlog_items": total_backlog_items,
        "total_orders_value": sum(order["total_value"] for order in filtered_orders)
    }

@app.get("/api/spending/summary")
def get_spending_summary():
    """Get spending summary statistics"""
    return spending_summary

@app.get("/api/spending/monthly")
def get_monthly_spending():
    """Get monthly spending breakdown"""
    return monthly_spending

@app.get("/api/spending/categories")
def get_category_spending():
    """Get spending by category"""
    return category_spending

@app.get("/api/spending/transactions")
def get_recent_transactions():
    """Get recent transactions"""
    return recent_transactions

@app.get("/api/reports/quarterly")
def get_quarterly_reports():
    """Get quarterly performance reports"""
    # Calculate quarterly statistics from orders
    quarters = {}

    for order in orders:
        order_date = order.get('order_date', '')
        # Determine quarter
        if '2025-01' in order_date or '2025-02' in order_date or '2025-03' in order_date:
            quarter = 'Q1-2025'
        elif '2025-04' in order_date or '2025-05' in order_date or '2025-06' in order_date:
            quarter = 'Q2-2025'
        elif '2025-07' in order_date or '2025-08' in order_date or '2025-09' in order_date:
            quarter = 'Q3-2025'
        elif '2025-10' in order_date or '2025-11' in order_date or '2025-12' in order_date:
            quarter = 'Q4-2025'
        else:
            continue

        if quarter not in quarters:
            quarters[quarter] = {
                'quarter': quarter,
                'total_orders': 0,
                'total_revenue': 0,
                'delivered_orders': 0,
                'avg_order_value': 0
            }

        quarters[quarter]['total_orders'] += 1
        quarters[quarter]['total_revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            quarters[quarter]['delivered_orders'] += 1

    # Calculate averages and fulfillment rate
    result = []
    for q, data in quarters.items():
        if data['total_orders'] > 0:
            data['avg_order_value'] = round(data['total_revenue'] / data['total_orders'], 2)
            data['fulfillment_rate'] = round((data['delivered_orders'] / data['total_orders']) * 100, 1)
        result.append(data)

    # Sort by quarter
    result.sort(key=lambda x: x['quarter'])
    return result

@app.get("/api/reports/monthly-trends")
def get_monthly_trends():
    """Get month-over-month trends"""
    months = {}

    for order in orders:
        order_date = order.get('order_date', '')
        if not order_date:
            continue

        # Extract month (format: YYYY-MM-DD)
        month = order_date[:7]  # Gets YYYY-MM

        if month not in months:
            months[month] = {
                'month': month,
                'order_count': 0,
                'revenue': 0,
                'delivered_count': 0
            }

        months[month]['order_count'] += 1
        months[month]['revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            months[month]['delivered_count'] += 1

    # Convert to list and sort
    result = list(months.values())
    result.sort(key=lambda x: x['month'])
    return result

# ---------------------------------------------------------------------------
# Restocking
# ---------------------------------------------------------------------------

DEFAULT_LEAD_TIME_DAYS = 10
ORDER_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _compute_lead_times():
    """Median order_date -> expected_delivery gap, in days, per category.

    Derived from the historical order set rather than hard-coded so the figure
    stays truthful if the fixtures change. Median (not mean) because a single
    mis-dated record would drag an average badly. Computed once at import: the
    baseline must describe delivered history, so restock orders appended at
    runtime deliberately do not feed back into it.
    """
    spans = {}
    for order in orders:
        try:
            placed = datetime.strptime(order["order_date"], ORDER_DATE_FORMAT)
            due = datetime.strptime(order["expected_delivery"], ORDER_DATE_FORMAT)
        except (KeyError, ValueError):
            continue
        spans.setdefault(order.get("category"), []).append((due - placed).days)

    by_category = {c: int(round(statistics.median(v))) for c, v in spans.items() if c}
    every_span = [d for v in spans.values() for d in v]
    overall = int(round(statistics.median(every_span))) if every_span else DEFAULT_LEAD_TIME_DAYS
    return by_category, overall


LEAD_TIMES_BY_CATEGORY, OVERALL_LEAD_TIME_DAYS = _compute_lead_times()


def get_lead_time_for_sku(sku: str) -> int:
    """Lead time for a forecast SKU, via its inventory category when one exists.

    Only PSU-501 of the nine forecast SKUs currently appears in inventory.json --
    the two catalogues are otherwise disjoint -- so most items fall through to
    the overall median.
    """
    for item in inventory_items:
        if item["sku"] == sku:
            category = item.get("category")
            return LEAD_TIMES_BY_CATEGORY.get(category, OVERALL_LEAD_TIME_DAYS)
    return OVERALL_LEAD_TIME_DAYS


def build_recommendations(budget: float):
    """Greedy allocation of a budget across forecast shortfalls.

    Items are ranked by unmet demand (forecasted - current) and funded in that
    order. An item whose full shortfall does not fit in the remaining budget is
    still bought partially, down to whatever whole units fit, and flagged
    fully_funded=False -- a part-funded line is a real answer, not an error.
    Zero-unit lines are dropped so the table never shows an empty row.
    """
    candidates = []
    for forecast in demand_forecasts:
        shortfall = forecast["forecasted_demand"] - forecast["current_demand"]
        if shortfall <= 0:
            continue
        candidates.append({
            "item_sku": forecast["item_sku"],
            "item_name": forecast["item_name"],
            "shortfall": shortfall,
            "unit_cost": forecast["unit_cost"],
            "lead_time_days": get_lead_time_for_sku(forecast["item_sku"]),
        })

    candidates.sort(key=lambda c: c["shortfall"], reverse=True)

    remaining = max(budget, 0)
    recommendations = []
    for candidate in candidates:
        affordable = int(remaining // candidate["unit_cost"])
        quantity = min(candidate["shortfall"], affordable)
        if quantity <= 0:
            continue
        line_total = round(quantity * candidate["unit_cost"], 2)
        remaining = round(remaining - line_total, 2)
        recommendations.append({
            **candidate,
            "recommended_quantity": quantity,
            "line_total": line_total,
            "fully_funded": quantity == candidate["shortfall"],
        })

    total_cost = round(sum(r["line_total"] for r in recommendations), 2)
    cost_to_cover_all = round(
        sum(c["shortfall"] * c["unit_cost"] for c in candidates), 2
    )
    return {
        "budget": round(budget, 2),
        "total_cost": total_cost,
        "budget_remaining": round(max(budget, 0) - total_cost, 2),
        "items_recommended": len(recommendations),
        "cost_to_cover_all": cost_to_cover_all,
        "recommendations": recommendations,
    }


@app.get("/api/restocking/recommendations")
def get_restocking_recommendations(budget: float = 0):
    """Recommend forecast items to restock within a budget"""
    return build_recommendations(budget)


class RestockOrderItem(BaseModel):
    item_sku: str
    item_name: str
    quantity: int
    unit_cost: float


class RestockOrderRequest(BaseModel):
    items: List[RestockOrderItem]


@app.post("/api/orders/restock", response_model=Order)
def submit_restock_order(request: RestockOrderRequest):
    """Create an order from a restocking selection and add it to the order list"""
    if not request.items:
        raise HTTPException(status_code=400, detail="No items to order")
    if any(item.quantity <= 0 for item in request.items):
        raise HTTPException(status_code=400, detail="Quantities must be greater than zero")

    # Numeric ids and ORD-2025-NNNN numbers are assigned sequentially, matching
    # the existing fixtures. max() rather than len() so the sequence still holds
    # after several restock orders have been appended.
    next_id = max((int(o["id"]) for o in orders if o["id"].isdigit()), default=0) + 1

    lead_time = max(
        (get_lead_time_for_sku(item.item_sku) for item in request.items),
        default=OVERALL_LEAD_TIME_DAYS,
    )
    placed = datetime.now().replace(second=0, microsecond=0)

    # Orders carry unit_price; the forecast carries unit_cost. Same number,
    # different field name, and /api/orders consumers expect the order spelling.
    items = [
        {
            "sku": item.item_sku,
            "name": item.item_name,
            "quantity": item.quantity,
            "unit_price": item.unit_cost,
        }
        for item in request.items
    ]

    order = {
        "id": str(next_id),
        "order_number": f"ORD-2025-{next_id:04d}",
        "customer": "Internal Restocking",
        "items": items,
        "status": "Processing",
        "order_date": placed.strftime(ORDER_DATE_FORMAT),
        "expected_delivery": (placed + timedelta(days=lead_time)).strftime(ORDER_DATE_FORMAT),
        "total_value": round(sum(i["quantity"] * i["unit_price"] for i in items), 2),
        "is_restock": True,
        "lead_time_days": lead_time,
    }
    orders.append(order)
    return order


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
