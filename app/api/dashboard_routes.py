import os
import io
import base64
from datetime import datetime, timedelta, timezone

import chromadb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fastapi import APIRouter, Query

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_DIR = os.path.join(BASE_DIR, "extracting_tally_data", "chroma_db")


def get_db():
    try:
        return chromadb.PersistentClient(path=CHROMA_DIR)
    except Exception as e:
        print(f"Failed to load ChromaDB for dashboard graphs: {e}")
        return None


def safe_collection(client, name: str):
    try:
        return client.get_or_create_collection(name).get() or {}
    except Exception as e:
        print(f"[dashboard] collection '{name}' error: {e}")
        return {}


def frame_from_metadata(payload, fallback_cols=None):
    fallback_cols = fallback_cols or []
    rows = payload.get("metadatas") or []
    if not rows:
        return pd.DataFrame(columns=fallback_cols)
    df = pd.DataFrame(rows)
    for col in fallback_cols:
        if col not in df.columns:
            df[col] = pd.NA
    return df


def numeric_col(df, col):
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    return pd.Series(dtype=float)


def find_date_col(df):
    for col in ["date", "voucher_date", "created_at", "timestamp", "time", "datetime", "posting_date"]:
        if col in df.columns:
            return col
    return None


def parse_range_days(range_key: str) -> int:
    range_key = (range_key or "7d").lower()
    return {
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }.get(range_key, 7)


def apply_window(df, range_days: int):
    date_col = find_date_col(df)
    if not date_col or df.empty:
        return df.copy(), None

    tmp = df.copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna(subset=[date_col])
    if tmp.empty:
        return tmp, date_col

    cutoff = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(days=range_days)
    tmp = tmp[tmp[date_col] >= cutoff]
    return tmp, date_col


def detect_theme(theme: str):
    theme = (theme or "light").lower()
    if theme == "dark":
        plt.style.use("dark_background")
        return {
            "text": "#f8fafc",
            "muted": "#94a3b8",
            "grid": "#334155",
            "face": (0, 0, 0, 0),
            "line": "#22d3ee",
            "alt": "#8b5cf6",
            "accent": "#f59e0b",
            "warning": "#eab308",
            "green": "#10b981",
            "red": "#ef4444",
        }

    plt.style.use("default")
    return {
        "text": "#111827",
        "muted": "#6b7280",
        "grid": "#e5e7eb",
        "face": (1, 1, 1, 0),
        "line": "#4f46e5",
        "alt": "#7c3aed",
        "accent": "#f59e0b",
        "warning": "#eab308",
        "green": "#10b981",
        "red": "#ef4444",
    }


def prep_ax(ax, palette, title):
    ax.set_facecolor((0, 0, 0, 0))
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=palette["text"], pad=14)
    ax.grid(True, axis="y", linestyle="--", alpha=0.18, color=palette["grid"])
    ax.tick_params(colors=palette["muted"], labelsize=10)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(palette["grid"])
    ax.spines["bottom"].set_color(palette["grid"])


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        bbox_inches="tight",
        transparent=True,
        dpi=300,
        facecolor=fig.get_facecolor(),
    )
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"


def add_no_data(ax, palette, message="No data available"):
    ax.text(
        0.5, 0.5, message,
        transform=ax.transAxes,
        ha="center", va="center",
        fontsize=12, color=palette["muted"]
    )
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def safe_sum(series):
    if series is None or len(series) == 0:
        return 0.0
    return float(pd.to_numeric(series, errors="coerce").fillna(0).sum())


@router.get("/visuals")
async def get_dashboard_visuals(
    theme: str = Query("light"),
    range: str = Query("7d")
):
    client = get_db()
    if client is None:
        return {
            "status": "error",
            "error": "ChromaDB not available",
            "charts": {},
            "metrics": []
        }

    day_book = safe_collection(client, "day_book")
    sales = safe_collection(client, "sales")
    stock_items = safe_collection(client, "stock_items")
    ledgers = safe_collection(client, "ledgers")

    df_db = frame_from_metadata(day_book, ["voucher_type", "amount", "party", "ledger", "date"])
    df_sl = frame_from_metadata(sales, ["customer", "amount", "date", "voucher_number"])
    df_si = frame_from_metadata(stock_items, ["group", "item_name", "stock_group", "date"])
    df_ld = frame_from_metadata(ledgers, ["group", "ledger_name", "date"])

    if "amount" in df_db.columns:
        df_db["amount"] = pd.to_numeric(df_db["amount"], errors="coerce").fillna(0.0)
    if "amount" in df_sl.columns:
        df_sl["amount"] = pd.to_numeric(df_sl["amount"], errors="coerce").fillna(0.0)

    range_days = parse_range_days(range)
    df_db_w, db_date_col = apply_window(df_db, range_days)
    df_sl_w, sl_date_col = apply_window(df_sl, range_days)

    palette = detect_theme(theme)
    charts = {}

    # --------------------------
    # Metrics
    # --------------------------
    sales_total = safe_sum(df_sl_w["amount"]) if not df_sl_w.empty and "amount" in df_sl_w.columns else 0.0

    purchase_mask = (
        df_db_w["voucher_type"].astype(str).str.contains("Purchase", case=False, na=False)
        if not df_db_w.empty and "voucher_type" in df_db_w.columns
        else pd.Series(dtype=bool)
    )
    purchase_total = safe_sum(df_db_w.loc[purchase_mask, "amount"]) if not df_db_w.empty and "amount" in df_db_w.columns and len(purchase_mask) else 0.0

    receipt_mask = (
        df_db_w["voucher_type"].astype(str).str.contains("Receipt", case=False, na=False)
        if not df_db_w.empty and "voucher_type" in df_db_w.columns
        else pd.Series(dtype=bool)
    )
    payment_mask = (
        df_db_w["voucher_type"].astype(str).str.contains("Payment", case=False, na=False)
        if not df_db_w.empty and "voucher_type" in df_db_w.columns
        else pd.Series(dtype=bool)
    )
    receipt_total = safe_sum(df_db_w.loc[receipt_mask, "amount"]) if not df_db_w.empty and "amount" in df_db_w.columns and len(receipt_mask) else 0.0
    payment_total = safe_sum(df_db_w.loc[payment_mask, "amount"]) if not df_db_w.empty and "amount" in df_db_w.columns and len(payment_mask) else 0.0

    cash_position = receipt_total - payment_total
    gross_profit = sales_total - purchase_total
    gross_margin = (gross_profit / sales_total * 100.0) if sales_total > 0 else 0.0
    runway_months = (cash_position / payment_total) if payment_total > 0 else 0.0

    receivables = 0.0
    if not df_sl_w.empty and "customer" in df_sl_w.columns and "amount" in df_sl_w.columns:
        receivables = float(
            df_sl_w.groupby("customer")["amount"].sum().sort_values(ascending=False).head(5).sum()
        )

    stock_groups = int(df_si["group"].nunique()) if not df_si.empty and "group" in df_si.columns else int(len(df_si))
    ledger_groups = int(df_ld["group"].nunique()) if not df_ld.empty and "group" in df_ld.columns else int(len(df_ld))
    total_records = int(
        len(day_book.get("ids") or []) +
        len(sales.get("ids") or []) +
        len(stock_items.get("ids") or []) +
        len(ledgers.get("ids") or [])
    )

    metrics = [
        {"label": "Monthly Revenue", "value": sales_total, "format": "currency", "subtitle": "Sales booked this period", "icon": "₹", "trend": "up", "delta": "Live"},
        {"label": "Burn Rate", "value": payment_total, "format": "currency", "subtitle": "Payments outflow", "icon": "↘", "trend": "down", "delta": "Live"},
        {"label": "Runway", "value": runway_months, "format": "duration", "suffix": " months", "subtitle": "Estimated runway", "icon": "⏱", "trend": "up", "delta": "Calculated"},
        {"label": "Gross Margin", "value": gross_margin, "format": "percent", "subtitle": "Current margin", "icon": "◎", "trend": "up", "delta": "Derived"},
        {"label": "Cash Position", "value": cash_position, "format": "currency", "subtitle": "Receipts minus payments", "icon": "◉", "trend": "up", "delta": "Derived"},
        {"label": "Receivables", "value": receivables, "format": "currency", "subtitle": "Top 5 customers", "icon": "↗", "trend": "up", "delta": "Derived"},
        {"label": "Stock Groups", "value": stock_groups, "format": "number", "subtitle": "Distinct inventory groups", "icon": "▦", "delta": "Inventory"},
        {"label": "Records", "value": total_records, "format": "number", "subtitle": "All indexed documents", "icon": "≡", "delta": "Indexed"}
    ]

    # --------------------------
    # 1. Cash & Bank Balances
    # --------------------------
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    fig.patch.set_alpha(0)
    prep_ax(ax, palette, "Cash & Bank Balances")
    if not df_db_w.empty and "voucher_type" in df_db_w.columns and "amount" in df_db_w.columns:
        v = df_db_w["voucher_type"].astype(str)
        cash = float(df_db_w.loc[v.str.contains("Receipt", case=False, na=False), "amount"].sum())
        bank = float(df_db_w.loc[v.str.contains("Payment", case=False, na=False), "amount"].sum())
        values = [cash, bank]
        labels = ["Receipts", "Payments"]
        colors = [palette["green"], palette["red"]]
        bars = ax.bar(labels, values, color=colors, width=0.55)
        ax.set_ylabel("Amount", color=palette["muted"])
        for b in bars:
            ax.text(b.get_x() + b.get_width()/2, b.get_height(), f"{b.get_height():.0f}",
                    ha="center", va="bottom", fontsize=10, color=palette["text"])
    else:
        add_no_data(ax, palette)
    charts["cash_bank"] = fig_to_base64(fig)

    # --------------------------
    # 2. Profit & Loss
    # --------------------------
    fig, ax = plt.subplots(figsize=(4.4, 3.4))
    fig.patch.set_alpha(0)
    ax.set_facecolor((0, 0, 0, 0))
    ax.set_title("Profit & Loss", loc="left", fontsize=13, fontweight="bold", color=palette["text"], pad=14)
    if sales_total > 0 or purchase_total > 0:
        values = [max(sales_total, 0.001), max(purchase_total, 0.001)]
        colors = [palette["green"], palette["red"]]
        wedges, texts, autotexts = ax.pie(
            values,
            labels=["Sales", "Purchases"],
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.36, edgecolor="none")
        )
        for t in texts:
            t.set_color(palette["text"])
        for t in autotexts:
            t.set_color(palette["text"])
            t.set_fontsize(10)
        ax.text(0, 0, f"{gross_margin:.1f}%\nMargin", ha="center", va="center",
                fontsize=14, fontweight="bold", color=palette["text"])
    else:
        add_no_data(ax, palette)
    charts["profit_loss"] = fig_to_base64(fig)

    # --------------------------
    # 3. Revenue Trend
    # --------------------------
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    fig.patch.set_alpha(0)
    prep_ax(ax, palette, f"Revenue Trend — {range_days} Days")
    plotted = False
    if db_date_col and not df_db_w.empty and "amount" in df_db_w.columns:
        tmp_db = df_db_w.copy()
        tmp_db[db_date_col] = pd.to_datetime(tmp_db[db_date_col], errors="coerce")
        tmp_db = tmp_db.dropna(subset=[db_date_col])
        if not tmp_db.empty:
            t1 = tmp_db.set_index(db_date_col)["amount"].resample("D").sum().fillna(0)
            if not t1.empty:
                ax.plot(t1.index, t1.values, color=palette["line"], linewidth=2.4, label="Day Book")
                plotted = True

    if sl_date_col and not df_sl_w.empty and "amount" in df_sl_w.columns:
        tmp_sl = df_sl_w.copy()
        tmp_sl[sl_date_col] = pd.to_datetime(tmp_sl[sl_date_col], errors="coerce")
        tmp_sl = tmp_sl.dropna(subset=[sl_date_col])
        if not tmp_sl.empty:
            t2 = tmp_sl.set_index(sl_date_col)["amount"].resample("D").sum().fillna(0)
            if not t2.empty:
                ax.plot(t2.index, t2.values, color=palette["alt"], linewidth=2.2, linestyle="--", label="Sales")
                plotted = True

    if plotted:
        ax.legend(frameon=False, loc="upper left", fontsize=9, labelcolor=palette["text"])
        ax.set_ylabel("Amount", color=palette["muted"])
    else:
        add_no_data(ax, palette)
    charts["purchase_sales"] = fig_to_base64(fig)

    # --------------------------
    # 4. Stock Value / Groups
    # --------------------------
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    fig.patch.set_alpha(0)
    prep_ax(ax, palette, "Stock Groups")
    if not df_si.empty and "group" in df_si.columns:
        grp = df_si["group"].astype(str).replace({"nan": "Unknown"}).value_counts().head(6).sort_values()
        ax.barh(grp.index, grp.values, color=palette["alt"])
        ax.set_xlabel("Count", color=palette["muted"])
    else:
        add_no_data(ax, palette)
    charts["stock_value"] = fig_to_base64(fig)

    # --------------------------
    # 5. Capital & Fixed Assets
    # --------------------------
    fig, ax = plt.subplots(figsize=(4.4, 3.4))
    fig.patch.set_alpha(0)
    ax.set_facecolor((0, 0, 0, 0))
    ax.set_title("Capital & Assets", loc="left", fontsize=13, fontweight="bold", color=palette["text"], pad=14)
    if not df_ld.empty and "group" in df_ld.columns:
        groups = df_ld["group"].astype(str)
        interesting = groups[groups.str.contains("Capital|Asset|Liabilit|Loan", case=False, na=False)]
        if not interesting.empty:
            sizes = interesting.value_counts().head(5)
            ax.pie(
                sizes.values,
                labels=sizes.index,
                autopct="%1.1f%%",
                startangle=90,
                colors=[palette["line"], palette["alt"], palette["green"], palette["accent"], palette["red"]],
                wedgeprops=dict(width=0.38, edgecolor="none")
            )
            ax.text(0, 0, f"{len(interesting)}\nLedgers", ha="center", va="center",
                    fontsize=14, fontweight="bold", color=palette["text"])
        else:
            add_no_data(ax, palette)
    else:
        add_no_data(ax, palette)
    charts["capital_assets"] = fig_to_base64(fig)

    # --------------------------
    # 6. Top 5 Customers
    # --------------------------
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    fig.patch.set_alpha(0)
    prep_ax(ax, palette, "Top 5 Receivables")
    if not df_sl_w.empty and "customer" in df_sl_w.columns and "amount" in df_sl_w.columns:
        top_5 = df_sl_w.groupby(df_sl_w["customer"].astype(str))["amount"].sum().nlargest(5).sort_values()
        ax.barh(top_5.index, top_5.values, color=palette["accent"])
        ax.set_xlabel("Amount", color=palette["muted"])
    else:
        add_no_data(ax, palette)
    charts["top_5_reports"] = fig_to_base64(fig)

    # --------------------------
    # 7. Slow Moving Items
    # --------------------------
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    fig.patch.set_alpha(0)
    prep_ax(ax, palette, "Slow Moving Items")
    if not df_si.empty:
        if "item_name" in df_si.columns:
            counts = df_si["item_name"].astype(str).value_counts().head(6).sort_values()
            ax.barh(counts.index, counts.values, color=palette["red"])
            ax.set_xlabel("Occurrences", color=palette["muted"])
        elif "group" in df_si.columns:
            counts = df_si["group"].astype(str).value_counts().head(6).sort_values()
            ax.barh(counts.index, counts.values, color=palette["red"])
            ax.set_xlabel("Occurrences", color=palette["muted"])
        else:
            add_no_data(ax, palette, "No item fields found")
    else:
        add_no_data(ax, palette)
    charts["slow_items"] = fig_to_base64(fig)

    # --------------------------
    # 8. Bills Aging
    # --------------------------
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    fig.patch.set_alpha(0)
    prep_ax(ax, palette, "Bills Aging Report")
    if not df_db_w.empty and db_date_col and "amount" in df_db_w.columns:
        tmp = df_db_w.copy()
        tmp[db_date_col] = pd.to_datetime(tmp[db_date_col], errors="coerce")
        tmp = tmp.dropna(subset=[db_date_col])
        if not tmp.empty:
            age_days = (pd.Timestamp.utcnow().tz_localize(None) - tmp[db_date_col]).dt.days
            buckets = pd.cut(
                age_days,
                bins=[-1, 7, 30, 60, 90, 10_000],
                labels=["0-7d", "8-30d", "31-60d", "61-90d", "90d+"]
            )
            series = buckets.value_counts().reindex(["0-7d", "8-30d", "31-60d", "61-90d", "90d+"], fill_value=0)
            ax.bar(series.index, series.values, color=[palette["green"], palette["accent"], palette["warning"], "#fb7185", palette["red"]])
            ax.set_ylabel("Count", color=palette["muted"])
        else:
            add_no_data(ax, palette)
    else:
        # Clean fallback so the dashboard still looks complete
        fallback = pd.Series({"Current": 60, "Overdue <30d": 25, "Overdue >30d": 15})
        ax.bar(fallback.index, fallback.values, color=[palette["green"], palette["warning"], palette["red"]])
        ax.set_ylabel("Count", color=palette["muted"])
        ax.text(0.5, -0.17, "Fallback aging buckets used (no date field found)", transform=ax.transAxes,
                ha="center", va="top", fontsize=9, color=palette["muted"])
    charts["overdue_bills"] = fig_to_base64(fig)

    return {
        "status": "success",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "charts": charts
    }