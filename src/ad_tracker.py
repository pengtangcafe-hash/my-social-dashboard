"""
ad_tracker.py — ติดตาม Ad Campaign performance (Paid + Boost)

บันทึก: platform, service, budget, reach, leads, dates
คำนวณ: CPR, CPL, CTR, ROAS
inject AD_CAMPAIGNS เข้า dashboard HTML

Usage (CLI):
  python src/ad_tracker.py show
  python src/ad_tracker.py show-json
  python src/ad_tracker.py log facebook "จัดฟัน" 3000 [--days 14] [--objective leads]
  python src/ad_tracker.py update camp-001 --reach 15000 --leads 23 [--spend 2800]
  python src/ad_tracker.py inject dashboard/index.html
"""

import json
import re
import sys
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR     = PROJECT_ROOT / "data"
CAMPAIGNS_FILE = DATA_DIR / "ad-campaigns.json"

PLATFORMS = ["facebook", "tiktok", "instagram", "google", "line"]

PLATFORM_COLORS = {
    "facebook":  "#1877f2",
    "tiktok":    "#010101",
    "instagram": "#e1306c",
    "google":    "#4285f4",
    "line":      "#06c755",
}

OBJECTIVES = ["awareness", "leads", "conversion", "traffic", "engagement"]

# ── avg order value ต่อบริการ (สำหรับคำนวณ ROAS ถ้าไม่มีข้อมูลจริง)
AVG_ORDER_ESTIMATES = {
    "จัดฟัน": 30000,
    "จัดฟันใส": 45000,
    "รากเทียม": 35000,
    "ฟอกสีฟัน": 4500,
    "ขูดหินปูน": 600,
    "ครอบฟัน": 8000,
    "วีเนียร์": 6000,
    "default": 5000,
}


# ──────────────────────────────────────────────
# Load / Save
# ──────────────────────────────────────────────

def load_campaigns() -> dict:
    if CAMPAIGNS_FILE.exists():
        try:
            return json.loads(CAMPAIGNS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"campaigns": [], "last_updated": date.today().isoformat()}


def save_campaigns(data: dict) -> None:
    data["last_updated"] = date.today().isoformat()
    CAMPAIGNS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ──────────────────────────────────────────────
# Log new campaign
# ──────────────────────────────────────────────

def log_campaign(platform: str, service: str, budget: float,
                 days: int = 14, objective: str = "leads",
                 start_date: str | None = None,
                 notes: str = "") -> str:
    data = load_campaigns()
    campaign_id = f"camp-{len(data['campaigns']) + 1:03d}"
    sd = start_date or date.today().isoformat()
    ed = (datetime.fromisoformat(sd) + timedelta(days=days)).date().isoformat()

    entry = {
        "id":          campaign_id,
        "platform":    platform.lower(),
        "service":     service,
        "objective":   objective,
        "budget":      float(budget),
        "budget_spent": 0.0,
        "start_date":  sd,
        "end_date":    ed,
        "days":        days,
        "status":      "active",
        # Results (filled via update)
        "reach":       0,
        "impressions": 0,
        "clicks":      0,
        "leads":       0,
        "actual_revenue": 0.0,
        "notes":       notes,
        "created_at":  date.today().isoformat(),
    }
    data["campaigns"].append(entry)
    save_campaigns(data)

    print(f"✅ บันทึก campaign: {campaign_id}")
    print(f"   Platform: {platform.upper()}  |  บริการ: {service}")
    print(f"   Budget: {budget:,.0f} บาท  |  ระยะเวลา: {days} วัน ({sd} → {ed})")
    print(f"   Objective: {objective}")
    print(f"\n   อัปเดตผลลัพธ์: python src/ad_tracker.py update {campaign_id} --reach X --leads X")
    return campaign_id


# ──────────────────────────────────────────────
# Update campaign results
# ──────────────────────────────────────────────

def update_campaign(campaign_id: str,
                    reach: int | None = None,
                    impressions: int | None = None,
                    clicks: int | None = None,
                    leads: int | None = None,
                    spend: float | None = None,
                    revenue: float | None = None,
                    status: str | None = None) -> bool:
    data = load_campaigns()
    for c in data["campaigns"]:
        if c["id"] == campaign_id:
            if reach is not None:       c["reach"] = reach
            if impressions is not None: c["impressions"] = impressions
            if clicks is not None:      c["clicks"] = clicks
            if leads is not None:       c["leads"] = leads
            if spend is not None:       c["budget_spent"] = spend
            if revenue is not None:     c["actual_revenue"] = revenue
            if status is not None:      c["status"] = status
            save_campaigns(data)
            print(f"✅ อัปเดต {campaign_id} แล้ว")
            _print_campaign_summary(c)
            return True
    print(f"❌ ไม่พบ campaign ID: {campaign_id}")
    return False


# ──────────────────────────────────────────────
# Compute KPIs
# ──────────────────────────────────────────────

def _compute_kpis(c: dict) -> dict:
    spent   = c.get("budget_spent") or c.get("budget", 0)
    reach   = c.get("reach", 0)
    impr    = c.get("impressions", 0) or reach
    clicks  = c.get("clicks", 0)
    leads   = c.get("leads", 0)
    revenue = c.get("actual_revenue", 0)

    # ถ้าไม่มี revenue จริง ประเมินจาก leads × avg order
    if revenue == 0 and leads > 0:
        avg = AVG_ORDER_ESTIMATES.get(
            c.get("service", ""), AVG_ORDER_ESTIMATES["default"]
        )
        revenue = leads * avg * 0.3  # assume 30% conversion rate จาก lead

    cpr  = round(spent / reach, 2) if reach > 0 else None
    cpl  = round(spent / leads, 0) if leads > 0 else None
    ctr  = round(clicks / impr * 100, 2) if impr > 0 else None
    roas = round(revenue / spent, 2) if spent > 0 and revenue > 0 else None

    return {
        "spent":   spent,
        "reach":   reach,
        "leads":   leads,
        "cpr":     cpr,
        "cpl":     cpl,
        "ctr":     ctr,
        "roas":    roas,
    }


def _print_campaign_summary(c: dict) -> None:
    kpis = _compute_kpis(c)
    print(f"\n  {'─'*48}")
    print(f"  {c['id']}  [{c['platform'].upper()}]  {c['service']}  ({c['status']})")
    print(f"  งบ: {c['budget']:,.0f} บาท  |  ใช้ไป: {kpis['spent']:,.0f} บาท  |  {c['start_date']} → {c['end_date']}")
    if kpis["reach"]:
        print(f"  Reach: {kpis['reach']:,}  |  Leads: {kpis['leads']}  |  "
              f"CPR: {kpis['cpr'] or '—'} บ  |  CPL: {kpis['cpl'] or '—'} บ  |  ROAS: {kpis['roas'] or '—'}x")


# ──────────────────────────────────────────────
# Show all campaigns
# ──────────────────────────────────────────────

def show_campaigns() -> None:
    data = load_campaigns()
    camps = data.get("campaigns", [])

    print("\n💰 Ad Campaign Tracker")
    print("═" * 55)

    if not camps:
        print("\n  ยังไม่มี campaign — ใช้ 'log' เพื่อเริ่มต้น")
        print("  ตัวอย่าง: python src/ad_tracker.py log facebook จัดฟัน 3000")
        print()
        return

    # Group by status
    active   = [c for c in camps if c.get("status") == "active"]
    ended    = [c for c in camps if c.get("status") != "active"]

    if active:
        print(f"\n  🟢 Active ({len(active)} campaign)")
        for c in active:
            _print_campaign_summary(c)

    if ended:
        print(f"\n  ⚫ Completed ({len(ended)} campaign)")
        for c in ended:
            _print_campaign_summary(c)

    # Total summary
    total_budget = sum(c.get("budget", 0) for c in camps)
    total_spent  = sum(c.get("budget_spent") or c.get("budget", 0) for c in camps)
    total_reach  = sum(c.get("reach", 0) for c in camps)
    total_leads  = sum(c.get("leads", 0) for c in camps)
    avg_cpl = round(total_spent / total_leads, 0) if total_leads > 0 else None

    print(f"\n  {'─'*48}")
    print(f"  TOTAL: งบรวม {total_budget:,.0f} บาท | ใช้ไป {total_spent:,.0f} | "
          f"Reach {total_reach:,} | Leads {total_leads}")
    if avg_cpl:
        print(f"  CPL เฉลี่ย: {avg_cpl:,.0f} บาท")
    print()


# ──────────────────────────────────────────────
# Build JS + inject dashboard
# ──────────────────────────────────────────────

def build_js_constant() -> str:
    data = load_campaigns()
    camps = data.get("campaigns", [])

    enriched = []
    for c in camps:
        kpis = _compute_kpis(c)
        enriched.append({**c, **kpis,
                         "color": PLATFORM_COLORS.get(c.get("platform", ""), "#94a3b8")})

    total_spent = sum(c.get("budget_spent") or c.get("budget", 0) for c in camps)
    total_reach = sum(c.get("reach", 0) for c in camps)
    total_leads = sum(c.get("leads", 0) for c in camps)

    payload = {
        "generated_at": date.today().isoformat(),
        "total_campaigns": len(camps),
        "total_spent":     total_spent,
        "total_reach":     total_reach,
        "total_leads":     total_leads,
        "avg_cpl":         round(total_spent / total_leads, 0) if total_leads > 0 else None,
        "campaigns":       enriched,
    }
    return f"const AD_CAMPAIGNS = {json.dumps(payload, ensure_ascii=False)};"


def inject_into_dashboard(html_path: str | Path) -> bool:
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"ไม่พบไฟล์: {html_path}")
        return False

    html     = html_path.read_text(encoding="utf-8")
    js_const = build_js_constant()
    marker   = "// ── Ad Campaign Data ──"

    pattern = r"const AD_CAMPAIGNS\s*=\s*\{[^;]*\};"
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, js_const, html, flags=re.DOTALL)
        print(f"✅ อัปเดต AD_CAMPAIGNS ใน {html_path.name}")
    elif marker in html:
        html = html.replace(marker, f"{marker}\n{js_const}", 1)
        print(f"✅ เพิ่ม AD_CAMPAIGNS ใน {html_path.name}")
    else:
        fallback = "// ── Content Category Data ──"
        if fallback in html:
            html = html.replace(fallback, f"{marker}\n{js_const}\n\n{fallback}", 1)
        else:
            html = html.replace("<script>", f"<script>\n{marker}\n{js_const}\n", 1)
        print(f"✅ เพิ่ม AD_CAMPAIGNS (fallback) ใน {html_path.name}")

    html_path.write_text(html, encoding="utf-8")
    return True


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]

    if not args or args[0] == "show":
        show_campaigns()

    elif args[0] == "show-json":
        data = load_campaigns()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args[0] == "inject" and len(args) >= 2:
        inject_into_dashboard(args[1])

    elif args[0] == "log" and len(args) >= 4:
        platform = args[1].lower()
        service  = args[2]
        try:
            budget = float(args[3].replace(",", ""))
        except ValueError:
            print("Budget ต้องเป็นตัวเลข เช่น 3000")
            sys.exit(1)

        days      = 14
        objective = "leads"
        start_dt  = None
        notes     = ""

        i = 4
        while i < len(args):
            if args[i] == "--days" and i + 1 < len(args):
                days = int(args[i + 1]); i += 2
            elif args[i] == "--objective" and i + 1 < len(args):
                objective = args[i + 1]; i += 2
            elif args[i] == "--start" and i + 1 < len(args):
                start_dt = args[i + 1]; i += 2
            elif args[i] == "--notes" and i + 1 < len(args):
                notes = args[i + 1]; i += 2
            else:
                i += 1

        log_campaign(platform, service, budget, days, objective, start_dt, notes)

    elif args[0] == "update" and len(args) >= 2:
        camp_id = args[1]
        reach = impressions = clicks = leads = None
        spend = revenue = None
        status = None

        i = 2
        while i < len(args):
            if args[i] == "--reach" and i + 1 < len(args):
                reach = int(args[i + 1]); i += 2
            elif args[i] == "--impressions" and i + 1 < len(args):
                impressions = int(args[i + 1]); i += 2
            elif args[i] == "--clicks" and i + 1 < len(args):
                clicks = int(args[i + 1]); i += 2
            elif args[i] == "--leads" and i + 1 < len(args):
                leads = int(args[i + 1]); i += 2
            elif args[i] == "--spend" and i + 1 < len(args):
                spend = float(args[i + 1]); i += 2
            elif args[i] == "--revenue" and i + 1 < len(args):
                revenue = float(args[i + 1]); i += 2
            elif args[i] == "--status" and i + 1 < len(args):
                status = args[i + 1]; i += 2
            else:
                i += 1

        update_campaign(camp_id, reach, impressions, clicks, leads, spend, revenue, status)

    else:
        print("Usage:")
        print("  python src/ad_tracker.py show")
        print("  python src/ad_tracker.py log facebook จัดฟัน 3000 [--days 14] [--objective leads]")
        print("  python src/ad_tracker.py update camp-001 --reach 15000 --leads 23 [--spend 2800]")
        print("  python src/ad_tracker.py inject dashboard/index.html")
        print()
        print(f"Platforms: {', '.join(PLATFORMS)}")
        print(f"Objectives: {', '.join(OBJECTIVES)}")
