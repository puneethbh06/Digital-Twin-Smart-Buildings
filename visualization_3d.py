# =============================================================================
# visualization_3d.py — 3-D Floor-Plan Visualization with Plotly
# =============================================================================
#
# PSEUDO-CODE OVERVIEW:
#
#   FUNCTION build_3d_floor_layout(df, building_name):
#
#       FILTER df → rows where building == building_name
#       IF empty:
#           RETURN empty Figure with "No data" title
#
#       FIND latest time-step in filtered data
#       SUB-SELECT only the most recent snapshot per room
#
#       CREATE Plotly Figure
#
#       ADD Scatter3d trace "Rooms":
#           x = room.x positions
#           y = room.y positions
#           z = room.floor (integer level)
#           marker size  ∝ occupancy (bigger = more people)
#           marker color = room_temp (colourscale: Viridis, cold→hot)
#           text labels  = room names
#
#       FOR each floor level:
#           ADD a rectangular outline trace to visually separate floors:
#               corners at (−0.5, −0.5) → (5.5, 2.5), z = floor level
#
#       CONFIGURE scene axes: X, Y, Floor
#       SET layout: title, height=600, minimal margins
#
#       RETURN fig
#
# =============================================================================

import plotly.graph_objects as go


def build_3d_floor_layout(df, building_name: str) -> go.Figure:
    """
    Build an interactive 3-D scatter plot showing all rooms in a building
    at the latest simulation time-step.

    Room markers are:
        - Sized  proportionally to occupancy (bigger = more people).
        - Coloured by current temperature (Viridis scale: cool→warm).
        - Labelled with the room name.

    Floor outlines are drawn as thin rectangular wireframes to give
    spatial context without cluttering the scene.

    Args:
        df            (pd.DataFrame): Full simulation dataset.
        building_name (str):          Building to visualise.

    Returns:
        go.Figure: Plotly 3-D figure ready for st.plotly_chart().
    """
    # --- PSEUDO: filter to selected building ---
    sub = df[df["building"] == building_name].copy()
    if sub.empty:
        return go.Figure().update_layout(title=f"No data for {building_name}")

    # --- PSEUDO: keep only the last recorded time-step ---
    latest_time = sub["time"].max()
    latest = sub[sub["time"] == latest_time].copy()

    fig = go.Figure()

    # --- PSEUDO: add one marker per room, coloured by temperature ---
    fig.add_trace(go.Scatter3d(
        x=latest["x"],
        y=latest["y"],
        z=latest["floor"],
        mode="markers+text",
        text=latest["room"],
        textposition="top center",
        marker=dict(
            size=10 + latest["occupancy"] / 4,   # occupancy → marker size
            color=latest["room_temp"],            # temperature → colour
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Temp °C"),
            opacity=0.9,
        ),
        name="Rooms",
    ))

    # --- PSEUDO: draw a floor outline rectangle for each level ---
    for f in sorted(latest["floor"].unique()):
        fig.add_trace(go.Scatter3d(
            x=[-0.5, 5.5, 5.5, -0.5, -0.5],
            y=[-0.5, -0.5, 2.5, 2.5, -0.5],
            z=[f] * 5,
            mode="lines",
            line=dict(color="rgba(120,120,120,0.35)", width=4),
            showlegend=False,
        ))

    # --- PSEUDO: configure 3-D scene and layout ---
    fig.update_layout(
        title=f"3D Floor Layout – {building_name}",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Floor",
            bgcolor="rgba(245,248,252,1)",
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=600,
    )
    return fig
