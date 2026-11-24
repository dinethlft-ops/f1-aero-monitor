"""
Formula 1 Cars - Speed & Aerodynamics Graphical Monitoring System
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time
from simulator import F1Simulator, CARS

# Page config
st.set_page_config(
    page_title="F1 Aero Monitor",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS - Dark F1 theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Titillium Web', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #0d0d0d 0%, #1a1a1a 100%);
    }
    
    h1, h2, h3 {
        color: #E10600 !important;
        font-weight: 700 !important;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #1e1e1e, #2a2a2a);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    
    .metric-value {
        font-size: 2.1rem;
        font-weight: 700;
        color: #ffffff;
        margin: 4px 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #aaaaaa;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .drs-on {
        color: #00ff88 !important;
        text-shadow: 0 0 10px #00ff88;
    }
    
    .drs-off {
        color: #666666 !important;
    }
    
    div[data-testid="stSidebar"] {
        background: #111111;
        border-right: 1px solid #333;
    }
    
    .stSelectbox label, .stRadio label {
        color: #cccccc !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_simulator():
    return F1Simulator()


def create_gauge(value, title, min_val, max_val, color, unit=""):
    """Create a Plotly gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": f" {unit}", "font": {"size": 28, "color": "white"}},
        title={"text": title, "font": {"size": 14, "color": "#aaaaaa"}},
        gauge={
            "axis": {"range": [min_val, max_val], "tickcolor": "#666"},
            "bar": {"color": color},
            "bgcolor": "#222",
            "borderwidth": 2,
            "bordercolor": "#444",
            "steps": [
                {"range": [min_val, max_val * 0.5], "color": "#1a1a1a"},
                {"range": [max_val * 0.5, max_val * 0.8], "color": "#252525"},
            ],
            "threshold": {
                "line": {"color": "#E10600", "width": 3},
                "thickness": 0.75,
                "value": max_val * 0.92
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        height=220,
        margin=dict(l=20, r=20, t=40, b=10)
    )
    return fig


def create_history_chart(hist, title, y_key, color, y_title):
    """Create a live line chart from history."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist["time"],
        y=hist[y_key],
        mode="lines",
        line=dict(color=color, width=2.5),
        fill="tozeroy",
        fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15)",
        name=y_title
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#cccccc")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#aaaaaa"),
        height=260,
        margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(showgrid=False, title="Time (s)"),
        yaxis=dict(showgrid=True, gridcolor="#333", title=y_title),
        showlegend=False
    )
    return fig


def main():
    st.markdown("# 🏎️ F1 Speed & Aerodynamics Monitor")
    st.caption("Real-time graphical monitoring system • Simulated telemetry • Aero forces calculated live")

    sim = get_simulator()

    # Sidebar controls
    with st.sidebar:
        st.markdown("### Controls")
        selected_number = st.selectbox(
            "Select Car",
            options=[c.number for c in CARS],
            format_func=lambda n: f"#{n} – {next(c.name for c in CARS if c.number == n)}",
            index=0
        )

        track = st.radio(
            "Track Type (affects Aero)",
            options=["balanced", "high_downforce", "low_drag"],
            format_func=lambda x: {
                "balanced": "⚖️ Balanced (e.g. Silverstone)",
                "high_downforce": "🔽 High Downforce (e.g. Monaco)",
                "low_drag": "➡️ Low Drag (e.g. Monza)"
            }[x],
            index=0
        )
        sim.set_track(track)

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This system simulates realistic F1 car telemetry and calculates 
        **aerodynamic forces** in real time using simplified physics equations.
        
        **Downforce & Drag** are derived from:
        - Current speed
        - Wing configuration
        - Track aero package
        - DRS status
        """)
        st.markdown("---")
        auto_refresh = st.checkbox("Auto-refresh (live)", value=True)

    # Update simulation
    sim.update()
    car = sim.get_car(selected_number)
    hist = sim.history[selected_number]

    # Header with car info
    col_info1, col_info2, col_info3 = st.columns([2, 2, 1])
    with col_info1:
        st.markdown(f"### #{car.number} {car.name}")
        st.markdown(f"**{car.team}**")
    with col_info2:
        drs_class = "drs-on" if car.drs else "drs-off"
        drs_text = "DRS OPEN" if car.drs else "DRS CLOSED"
        st.markdown(f"<div class='{drs_class}' style='font-size:1.4rem; font-weight:700; margin-top:12px;'>{drs_text}</div>", unsafe_allow_html=True)
    with col_info3:
        st.metric("Gear", f"{car.gear}")

    st.markdown("---")

    # Main metrics row
    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Speed</div>
            <div class="metric-value" style="color:#00d4ff;">{car.speed:.0f}</div>
            <div class="metric-label">km/h</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Downforce</div>
            <div class="metric-value" style="color:#00ff88;">{car.downforce:.0f}</div>
            <div class="metric-label">kg</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Drag Force</div>
            <div class="metric-value" style="color:#ff6b6b;">{car.drag:.0f}</div>
            <div class="metric-label">N</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Aero Efficiency</div>
            <div class="metric-value" style="color:#ffd700;">{car.aero_efficiency:.2f}</div>
            <div class="metric-label">L/D</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Engine RPM</div>
            <div class="metric-value" style="color:#ff9f43;">{car.rpm:.0f}</div>
            <div class="metric-label">rpm</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gauges
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.plotly_chart(create_gauge(car.speed, "Speed", 0, 360, "#00d4ff", "km/h"), use_container_width=True)
    with g2:
        st.plotly_chart(create_gauge(car.throttle, "Throttle", 0, 100, "#00ff88", "%"), use_container_width=True)
    with g3:
        st.plotly_chart(create_gauge(car.brake, "Brake", 0, 100, "#ff4757", "%"), use_container_width=True)
    with g4:
        st.plotly_chart(create_gauge(car.downforce, "Downforce", 0, 2500, "#a29bfe", "kg"), use_container_width=True)

    # History charts
    st.markdown("### Live Telemetry Traces")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            create_history_chart(hist, "Speed Over Time", "speed", "#00d4ff", "Speed (km/h)"),
            use_container_width=True
        )
    with c2:
        st.plotly_chart(
            create_history_chart(hist, "Downforce Over Time", "downforce", "#00ff88", "Downforce (kg)"),
            use_container_width=True
        )

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(
            create_history_chart(hist, "RPM Over Time", "rpm", "#ff9f43", "RPM"),
            use_container_width=True
        )
    with c4:
        st.plotly_chart(
            create_history_chart(hist, "Drag Force Over Time", "drag", "#ff6b6b", "Drag (N)"),
            use_container_width=True
        )

    # Secondary data
    st.markdown("### Vehicle Status")
    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown("**Tire Temperatures (°C)**")
        tire_df = pd.DataFrame({
            "Position": ["Front Left", "Front Right", "Rear Left", "Rear Right"],
            "Temp (°C)": [
                f"{car.tire_temp_fl:.1f}",
                f"{car.tire_temp_fr:.1f}",
                f"{car.tire_temp_rl:.1f}",
                f"{car.tire_temp_rr:.1f}"
            ]
        })
        st.dataframe(tire_df, hide_index=True, use_container_width=True)

    with s2:
        st.markdown("**Other Sensors**")
        st.metric("Engine Temp", f"{car.engine_temp:.1f} °C")
        st.metric("Lateral G", f"{car.lateral_g:.2f} G")
        st.metric("Fuel Remaining", f"{car.fuel:.1f} %")

    with s3:
        st.markdown("**Aero Package**")
        st.write(f"Track Setup: **{track.replace('_', ' ').title()}**")
        st.write(f"Wing Level: **{car._wing_level:.2f}**")
        st.write(f"DRS Active: **{'Yes' if car.drs else 'No'}**")

    with s4:
        st.markdown("**Leaderboard (Speed)**")
        all_cars = sorted(sim.get_all_cars(), key=lambda c: c.speed, reverse=True)
        for i, c in enumerate(all_cars[:5]):
            marker = "🟢" if c.number == selected_number else "⚪"
            st.write(f"{marker} {i+1}. #{c.number} {c.name[:12]} — **{c.speed:.0f}** km/h")

    # Footer
    st.markdown("---")
    st.caption("F1 Speed & Aerodynamics Graphical Monitoring System • Simulated data for educational / demo purposes • Not affiliated with Formula 1")

    # Auto refresh
    if auto_refresh:
        time.sleep(0.6)
        st.rerun()


if __name__ == "__main__":
    main()
