"""Advanced Analytics scavenger hunt application."""

from pathlib import Path
import json

import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.distance import geodesic

from models import State, Game, Location
from constants import STATE_FILE, GAME_FILE, LOGGING_FILE


# Get game files
game = Game.from_yaml_file(file_path=GAME_FILE)
state = State.from_yaml_file(file_path=STATE_FILE, game=game)

# Reload variables from state
if "index" not in st.session_state:
    st.session_state.index = 0


#############
# Scavenger #
#############
def scavenger_admin():
    """Scavenger hunt admin interface."""
    title_column_1, title_column_2 = st.columns([5, 1], vertical_alignment="bottom")
    with title_column_1:
        st.title("Scavenger hunt admin 🕵")
    with title_column_2:
        if st.button(label="Reload"):  # pragma: no cover
            st.rerun()

    overview_tab, questions_tab, stats_tab = st.tabs(["Overview", "Questions", "Statistics"])
    with overview_tab:
        ## Team statistics
        st.subheader("Team statistics")
        if state.n_active_teams > 0:
            st.write(f"Number of registered teams: {state.n_active_teams}")
            team_statistics = []
            for team in state.teams.values():
                current_goal = (
                    team.goal_location_name
                    if len(team.solved) < len(game.locations)
                    else "All locations solved"
                )
                team_statistics.append(
                    {
                        "Team": team.name,
                        # "Score": sum([score for score in team.solved.values()]),
                        "Solved": len(team.solved),
                        "Current goal": current_goal,
                    }
                )

            st.dataframe(team_statistics)
        else:
            st.write("No teams have registered yet.")

        ## Puzzle statistics
        st.subheader("Puzzle statistics")
        puzzle_statistics = []
        for ix, location in enumerate(game.locations):
            n_teams_solved = sum(1 for team in state.teams.values() if location.name in team.solved)
            n_teams_correct = sum(
                1
                for team in state.teams.values()
                if location.name in team.solved and team.solved[location.name] > 0
            )
            n_teams_incorrect = n_teams_solved - n_teams_correct
            puzzle_statistics.append(
                {
                    "Id": ix + 1,
                    "Location": location.name,
                    "Teams answered": n_teams_solved,
                    "Teams unanswered": state.n_active_teams - n_teams_solved,
                    "Teams correct": n_teams_correct,
                    "Teams incorrect": n_teams_incorrect,
                }
            )

        st.dataframe(data=puzzle_statistics, height=500)

        ## Danger zone
        st.subheader("Danger zone")
        st.markdown(
            "**Enable beam-to-location for all teams.** All teams will see a beam to location checkbox when their UI refreshes. When this checkbox is enabled, you are automatically beamed to the current goal and can directly answer the question."
        )

        def change_beam_to_location_if_state_exists(state: State, beam_to_location: bool):
            """Change beam to location visibility."""
            if (
                Path(STATE_FILE).exists()
                and state.button_beam_to_location_visible != beam_to_location
            ):
                state.button_beam_to_location_visible = beam_to_location
                state.save()

        beam_to_location_button_visible = st.checkbox(
            label="Show `beam-to-location` checkbox in user interface",
            value=state.button_beam_to_location_visible,
        )
        change_beam_to_location_if_state_exists(state, beam_to_location_button_visible)

        st.markdown("---")
        st.markdown(
            "**Delete all team data.** This will delete all team data and reset the game. This should only be done if nobody is actually logged in as each client can restore their version of the state"
        )
        if st.checkbox(label="Delete all team data"):
            if st.button(label="Confirm deletion"):
                state_folder = Path(STATE_FILE).parent
                for file in state_folder.glob("*"):
                    file.unlink()

                st.write("All team data has been deleted.")

    with questions_tab:
        selected_location: Location = game.locations[st.session_state.index]
        col1, col2, col3 = st.columns([4, 1, 1])

        with col1:
            st.subheader(f"{st.session_state.index + 1} - {selected_location.name}")

        with col2:

            def previous_item():
                """Select previous item."""
                st.session_state.index = (st.session_state.index - 1) % len(game.locations)

            st.button(label="Previous", on_click=previous_item)

        with col3:

            def next_item():
                """Select next item."""
                st.session_state.index = (st.session_state.index + 1) % len(game.locations)

            st.button(label="Next", on_click=next_item)

        base_question_path = Path(GAME_FILE).parent
        image_file = base_question_path / selected_location.image

        st.markdown(selected_location.question)
        if image_file.exists():
            st.image(str(image_file), use_container_width=True)

        st.subheader("Answer:")
        show_score = st.checkbox(label="Show score", value=False)
        for option in selected_location.answer:
            if show_score:
                st.write(f"Option: {option.option}, Score: {option.score}")
            else:
                st.write(f"Option: {option.option}")

    with stats_tab:
        ## Title
        st.subheader("Map")

        if not Path(LOGGING_FILE).exists():
            st.write("No logging file found.")
            return

        # load ndjson logging file
        with open(LOGGING_FILE, "r") as f:
            logs = pd.DataFrame([json.loads(line) for line in f])

        # Create map
        logs["timestamp"] = pd.to_datetime(logs["timestamp"])
        logs_sorted = logs.sort_values(by="timestamp")
        fig = px.line_mapbox(
            data_frame=logs_sorted,
            lat="latitude",
            lon="longitude",
            hover_name="current_goal",
            hover_data=["timestamp"],
            color="team_name",
            zoom=14.5,
            height=600,
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )
        fig.update_layout(
            mapbox={
                "style": "carto-positron",
            },
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
        )
        st.plotly_chart(fig)
        st.download_button(
            label="Download location statistics as CSV",
            data=logs_sorted.to_csv(),
            file_name="dataframe.csv",
            mime="text/csv",
        )

        ## Summary statistics
        st.subheader("Summary statistics")

        # Score
        scores_collected = {
            team_name: {
                location.name: team_state.solved[location.name]
                if location.name in team_state.solved
                else 0
                for location in game.locations
            }
            for team_name, team_state in state.teams.items()
        }
        scores = {
            team_name: sum(score for score in scores_collected[team_name].values())
            for team_name in scores_collected
        }

        # Distance statistics
        def calculate_distance(lat1, lon1, lat2, lon2):
            if pd.isnull(lat1) or pd.isnull(lon1) or pd.isnull(lat2) or pd.isnull(lon2):
                return 0
            return geodesic((lat1, lon1), (lat2, lon2)).kilometers

        logs_sorted["prev_latitude"] = logs_sorted["latitude"].shift()
        logs_sorted["prev_longitude"] = logs_sorted["longitude"].shift()
        no_beam_logs = logs_sorted[logs_sorted["beam_to_location"] == 0]
        beam_logs = logs_sorted[logs_sorted["beam_to_location"] == 1]
        no_beam_logs["distance"] = no_beam_logs.apply(
            lambda row: calculate_distance(
                row["latitude"], row["longitude"], row["prev_latitude"], row["prev_longitude"]
            ),
            axis=1,
        )
        beam_logs["distance"] = beam_logs.apply(
            lambda row: calculate_distance(
                row["latitude"], row["longitude"], row["prev_latitude"], row["prev_longitude"]
            ),
            axis=1,
        )

        summary_df = (
            logs_sorted.groupby("team_name")
            .apply(
                lambda group: pd.Series(
                    {
                        "points_clicked": no_beam_logs[
                            no_beam_logs["team_name"] == group.name
                        ].shape[0],
                        "distance_traveled": no_beam_logs[no_beam_logs["team_name"] == group.name][
                            "distance"
                        ].sum(),
                        "distance_beamed": beam_logs[beam_logs["team_name"] == group.name][
                            "distance"
                        ].sum(),
                        "total_score": scores[group.name] if group.name in scores else 0,
                    }
                ),
                include_groups=False,
            )
            .sort_values(by="total_score", ascending=False)
        )

        st.dataframe(summary_df)
        st.download_button(
            label="Download summary statistics as CSV",
            data=summary_df.to_csv(),
            file_name="dataframe.csv",
            mime="text/csv",
        )


########
# Main #
########
scavenger_admin()
