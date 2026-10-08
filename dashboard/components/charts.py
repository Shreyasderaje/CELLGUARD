import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Industrial Dark Theme Constants
BG_COLOR = "#0F172A"
PAPER_COLOR = "rgba(0,0,0,0)"
TEXT_COLOR = "#94A3B8"
GRID_COLOR = "#1E293B"

def create_defect_rate_chart(df_process):
    """
    Creates an interactive Plotly bar chart for Defect Rate by Machine Workstation
    with target benchmark line and machine-specific status colors.
    """
    if df_process.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_COLOR, plot_bgcolor=BG_COLOR)
        return fig

    rates = df_process.groupby("machine_id")["defect_status"].apply(lambda s: (s == "Defect").mean() * 100).reset_index()
    rates.columns = ["machine_id", "defect_rate"]

    colors = []
    status_labels = []
    for r in rates["defect_rate"]:
        if r > 18:
            colors.append("#EF4444")
            status_labels.append("CRITICAL")
        elif r > 12:
            colors.append("#F59E0B")
            status_labels.append("WARNING")
        else:
            colors.append("#38BDF8")
            status_labels.append("OPTIMAL")

    rates["status"] = status_labels

    fig = go.Figure()

    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(rates) - 0.5,
        y0=2.0,
        y1=2.0,
        line=dict(color="#10B981", width=2, dash="dash"),
        name="QC Benchmark (< 2.0%)"
    )

    fig.add_trace(
        go.Bar(
            x=rates["machine_id"],
            y=rates["defect_rate"],
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.15)", width=1)
            ),
            text=[f"{val:.1f}%" for val in rates["defect_rate"]],
            textposition="outside",
            textfont=dict(color="#F8FAFC", size=12, family="Inter, Segoe UI"),
            customdata=rates["status"],
            hovertemplate=(
                "<b>Workstation %{x}</b><br/>" +
                "Defect Rate: <b>%{y:.2f}%</b><br/>" +
                "Status: <b>%{customdata}</b><extra></extra>"
            ),
            name="Defect Rate"
        )
    )

    fig.update_layout(
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        margin=dict(l=20, r=20, t=30, b=30),
        height=320,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#CBD5E1", size=11)
        ),
        xaxis=dict(
            title=dict(text="Machine Workstation", font=dict(color=TEXT_COLOR, size=11)),
            tickfont=dict(color="#F8FAFC", size=11),
            showgrid=False,
            linecolor=GRID_COLOR
        ),
        yaxis=dict(
            title=dict(text="Defect Rate (%)", font=dict(color=TEXT_COLOR, size=11)),
            tickfont=dict(color="#CBD5E1", size=11),
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            range=[0, max(rates["defect_rate"].max() * 1.25, 5)]
        ),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_family="Inter, Segoe UI",
            font_color="#F8FAFC"
        )
    )

    return fig

def create_defect_pareto_chart(df_process):
    """
    Creates an interactive Plotly horizontal bar chart for Weld Defect Pareto Breakdown.
    """
    if df_process.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_COLOR, plot_bgcolor=BG_COLOR)
        return fig

    defect_counts = df_process[df_process["defect_type"] != "None"]["defect_type"].value_counts().reset_index()
    defect_counts.columns = ["defect_type", "count"]
    
    total_defects = defect_counts["count"].sum()
    defect_counts["percentage"] = (defect_counts["count"] / total_defects * 100) if total_defects > 0 else 0

    defect_counts = defect_counts.sort_values(by="count", ascending=True)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=defect_counts["defect_type"],
            x=defect_counts["count"],
            orientation="h",
            marker=dict(
                color="#38BDF8",
                line=dict(color="#1E3A8A", width=1)
            ),
            text=[f" {cnt:,} ({pct:.1f}%)" for cnt, pct in zip(defect_counts["count"], defect_counts["percentage"])],
            textposition="outside",
            textfont=dict(color="#F8FAFC", size=11, family="Inter, Segoe UI"),
            customdata=defect_counts["percentage"],
            hovertemplate=(
                "<b>Defect Type: %{y}</b><br/>" +
                "Occurrences: <b>%{x:,}</b><br/>" +
                "Share of Defects: <b>%{customdata:.1f}%</b><extra></extra>"
            )
        )
    )

    fig.update_layout(
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        margin=dict(l=20, r=40, t=20, b=30),
        height=320,
        showlegend=False,
        xaxis=dict(
            title=dict(text="Occurrences Count", font=dict(color=TEXT_COLOR, size=11)),
            tickfont=dict(color="#CBD5E1", size=11),
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            range=[0, max(defect_counts["count"].max() * 1.3, 10)]
        ),
        yaxis=dict(
            title=dict(text="Defect Category", font=dict(color=TEXT_COLOR, size=11)),
            tickfont=dict(color="#F8FAFC", size=11),
            showgrid=False,
            linecolor=GRID_COLOR
        ),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_family="Inter, Segoe UI",
            font_color="#F8FAFC"
        )
    )

    return fig

def create_quality_trend_chart(df_filtered):
    """
    Creates an interactive Plotly time-series trend line chart for Quality Time Machine.
    """
    if df_filtered.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_COLOR, plot_bgcolor=BG_COLOR)
        return fig

    df_copy = df_filtered.copy()
    df_copy["batch_group"] = (np.arange(len(df_copy)) // 50) * 50
    trend_df = df_copy.groupby("batch_group").agg(
        total_batches=("defect_status", "count"),
        defects_count=("defect_status", lambda s: (s == "Defect").sum())
    ).reset_index()

    trend_df["defect_rate"] = (trend_df["defects_count"] / trend_df["total_batches"]) * 100

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=trend_df["batch_group"],
            y=trend_df["defects_count"],
            mode="lines+markers",
            name="Defect Count",
            line=dict(color="#EF4444", width=2.5, shape="spline"),
            marker=dict(size=6, color="#FCA5A5", symbol="circle"),
            hovertemplate="Batch Group %{x}: <b>%{y} defects</b><extra></extra>"
        )
    )

    fig.update_layout(
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        margin=dict(l=20, r=20, t=20, b=30),
        height=320,
        showlegend=False,
        xaxis=dict(
            title=dict(text="Batch Group Sequence", font=dict(color=TEXT_COLOR, size=11)),
            tickfont=dict(color="#CBD5E1", size=11),
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR
        ),
        yaxis=dict(
            title=dict(text="Defects per Batch Group", font=dict(color=TEXT_COLOR, size=11)),
            tickfont=dict(color="#CBD5E1", size=11),
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR
        ),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_family="Inter, Segoe UI",
            font_color="#F8FAFC"
        )
    )

    return fig

def create_parameter_dist_chart(df_filtered, param_choice):
    """
    Creates an interactive Plotly histogram comparing Normal vs Defect batches parameter distribution.
    """
    if df_filtered.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=PAPER_COLOR, plot_bgcolor=BG_COLOR)
        return fig

    normal_data = df_filtered[df_filtered["defect_status"] == "Normal"][param_choice]
    defect_data = df_filtered[df_filtered["defect_status"] == "Defect"][param_choice]

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=normal_data,
            name="Normal Batches",
            marker_color="#10B981",
            opacity=0.6,
            nbinsx=35,
            hovertemplate="Normal Range %{x}: <b>%{y} count</b><extra></extra>"
        )
    )

    fig.add_trace(
        go.Histogram(
            x=defect_data,
            name="Defect Batches",
            marker_color="#EF4444",
            opacity=0.7,
            nbinsx=35,
            hovertemplate="Defect Range %{x}: <b>%{y} count</b><extra></extra>"
        )
    )

    fig.update_layout(
        barmode="overlay",
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        margin=dict(l=20, r=20, t=30, b=30),
        height=320,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#CBD5E1", size=11)
        ),
        xaxis=dict(
            title=dict(text=param_choice.upper(), font=dict(color=TEXT_COLOR, size=11)),
            tickfont=dict(color="#CBD5E1", size=11),
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR
        ),
        yaxis=dict(
            title=dict(text="Frequency Count", font=dict(color=TEXT_COLOR, size=11)),
            tickfont=dict(color="#CBD5E1", size=11),
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR
        ),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_family="Inter, Segoe UI",
            font_color="#F8FAFC"
        )
    )

    return fig
