import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import mplsoccer
from mplsoccer.pitch import Pitch
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors

import io
from matplotlib import pyplot as plt

if st.button("Refresh Data"):
        st.cache_data.clear()

DOCUMENT_ID = '11GOW9_pzJmAAAlvWKFYdh7YCc0lF4U7w'


@st.cache_data
def fetch_data(sheet_name):
    url = f'https://docs.google.com/spreadsheets/d/{DOCUMENT_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    return pd.read_csv(url)

# def download_plot(fig, file_name, mime="image/png", facecolor=None):
#     """Downloads a Matplotlib figure as a PNG image.

#     Args:
#         fig (matplotlib.figure.Figure): The figure to download.
#         file_name (str): The desired filename for the downloaded image.
#         mime (str, optional): The MIME type of the image. Defaults to "image/png".
#         facecolor (str, optional): The background color for the plot (used for heatmaps). Defaults to None.
#     """
#     buffer = io.BytesIO()
#     if facecolor:
#         # Set background color for heatmaps
#         fig.set_facecolor(facecolor)
#     fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
#     buffer.seek(0)
#     st.download_button(
#         label="Download",
#         data=buffer,
#         file_name=file_name,
#         mime=mime
#     )




def add_logo_on_heatmap(ax, logo_path, zoom=0.05, x_pos=0.85, y_pos=0.85, alpha=0.3):
    """Add a small, faint logo on the heatmap."""
    logo_img = plt.imread(logo_path)
    image_box = OffsetImage(logo_img, zoom=zoom, alpha=alpha)
    ab = AnnotationBbox(image_box, (x_pos, y_pos), frameon=False, xycoords='axes fraction')
    ax.add_artist(ab)


def create_team_heatmap(df_pass):
    st.sidebar.header("Select Team for Heatmap")
    st.header("Team Heatmap on Football Pitch")

    game_options = ["All Games"] + df_pass["Game"].unique().tolist()
    selected_game = st.sidebar.selectbox("Select Game:", game_options)

    # Step 1: Team selection
    team_heat = st.sidebar.selectbox("Select a team:", df_pass["Team"].unique())

    # Step 2: Game selection (add a new filter)
    

    # Filter data for the selected team and game
    if selected_game == "All Games":
        team_data = df_pass[df_pass["Team"] == team_heat]
    else:
        team_data = df_pass[(df_pass["Team"] == team_heat) & (df_pass["Game"] == selected_game)]

    # Create the heatmap plot
    fig_heat, ax = plt.subplots(figsize=(6, 4))
    fig_heat.set_facecolor('#22312b')
    ax.patch.set_facecolor('#22312b')
    ax.set_title(f'{team_heat} Team Heatmap - {selected_game}', color='white', fontsize=10, pad=20)

    # Create the pitch
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    pitch.draw(ax=ax)
    plt.gca().invert_yaxis()

    custom_colors = [(0, 'purple'), (0.5, 'yellow'), (1, 'red')]

    # Create custom colormap
    custom_cmap = mcolors.LinearSegmentedColormap.from_list("", custom_colors)

    # Generate heatmap
    sns.kdeplot(
        x=team_data['x'],
        y=team_data['y'],
        color='red',
        # fill=True,
        alpha=0.7,
        levels=10,
        cmap=custom_cmap,
        n_levels=40,
        shade=True,
        ax=ax
    )

    # Set pitch boundaries
    plt.xlim(0, 120)
    plt.ylim(0, 80)
    add_logo_on_heatmap(ax, "lagos-liga-blue.png", zoom=0.02, x_pos=0.5, y_pos=0.5, alpha=0.15)


    # Display the heatmap in Streamlit
    st.pyplot(fig_heat)
    # download_plot(fig_heat, f"{team_heat}_heatmap.png", facecolor=pitch.pitch_color)

df_new = fetch_data("shoot")

# Streamlit interface
st.sidebar.header("Team Shot Analysis")



# Get unique teams from the data
teams = df_new["team"].unique()

# Define team colors dynamically based on the teams in the data
team_colors = {team: f"C{i+1:02d}0{i+1:02d}" for i, team in enumerate(teams)}

# Team selection
team1 = st.sidebar.selectbox("Select Team 1", teams, index=0)
team2 = st.sidebar.selectbox("Select Team 2", teams, index = 1)

# Split df into two parts, one for each team
team1_df = df_new[df_new["team"] == team1].copy()
team2_df = df_new[df_new["team"] == team2].copy()

# Split into goals and non-goals for each team
team1_df_g = team1_df[team1_df["outcome"] == "Goal"].copy()
team1_df_ng = team1_df[team1_df["outcome"] != "Goal"].copy()

team2_df_g = team2_df[team2_df["outcome"] == "Goal"].copy()
team2_df_ng = team2_df[team2_df["outcome"] != "Goal"].copy()

# Team stats
team1_tot_shots = team1_df.shape[0]
team1_tot_goals = team1_df_g.shape[0]
team1_tot_xg = team1_df["statsbomb_xg"].sum().round(2)

team2_tot_shots = team2_df.shape[0]
team2_tot_goals = team2_df_g.shape[0]
team2_tot_xg = team2_df["statsbomb_xg"].sum().round(2)



pitch = Pitch(pitch_type='statsbomb', pitch_color='green', line_color='white', goal_type='box')

# Create the figure
fig, ax = pitch.draw(figsize=(7, 6))

# Title
ax.set_title(f"{team1} vs {team2} Shot Map", fontsize=10, pad=5)

# Plot Team 1 shots (shooting towards the right goal)
# Goals
pitch.scatter(team1_df_g["start_location_x"],
              team1_df_g["start_location_y"],
              s=team1_df_g["statsbomb_xg"] * 500 + 100,
              marker="football",
              c="blue",
              label=f"{team1} goals",
              ax=ax)
# Non-goals
pitch.scatter(team1_df_ng["start_location_x"],
              team1_df_ng["start_location_y"],
              s=team1_df_ng["statsbomb_xg"] * 500 + 100,
              c="red",
              alpha=0.5,
              hatch="//",
              edgecolor="#101010",
              marker="s",
              label=f"{team1} non-goals",
              ax=ax)

# Plot Team 2 shots (shooting towards the left goal)
# Goals
pitch.scatter(120 - team2_df_g["start_location_x"],  # Mirroring x-coordinates for the other direction
              team2_df_g["start_location_y"],
              s=team2_df_g["statsbomb_xg"] * 500 + 100,
              marker="football",
              c="cyan",
              label=f"{team2} goals",
              ax=ax)
# Non-goals
pitch.scatter(120 - team2_df_ng["start_location_x"],  # Mirroring x-coordinates for the other direction
              team2_df_ng["start_location_y"],
              s=team2_df_ng["statsbomb_xg"] * 500 + 100,
              c="orange",
              alpha=0.5,
              hatch="//",
              edgecolor="#101010",
              marker="s",
              label=f"{team2} non-goals",
              ax=ax)

# Add basic info for each team at the bottom
basic_info_txt = (
    f"{team1} - Shots: {team1_tot_shots} | Goals: {team1_tot_goals} | xG: {team1_tot_xg}\n"
    f"{team2} - Shots: {team2_tot_shots} | Goals: {team2_tot_goals} | xG: {team2_tot_xg}"
)
fig.text(0.5, 0.02, basic_info_txt, fontsize=5, ha="center", color="white")

# Add legend
ax.legend(labelspacing=2, loc="upper center", fontsize=5, bbox_to_anchor=(0.5, -0.05), ncol=2)

# Display the plot
add_logo_on_heatmap(ax, "lagos-liga-blue.png", zoom=0.02, x_pos=0.5, y_pos=0.5, alpha=0.15)
st.pyplot(fig)

# download_plot(fig, f"{team1}_vs_{team2}_shot_map.png")
def main():
    

    df_pass = fetch_data("Passes")
    create_team_heatmap(df_pass)

    





if __name__ == "__main__":
    main()