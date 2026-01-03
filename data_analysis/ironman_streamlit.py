import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Ironman Results Analysis", layout="wide")
st.title("Ironman Results Analysis Dashboard")
st.sidebar.header("Race Selection")

races = {
    "Nice 70.3 - 2025": "9718158a-07b2-4ab6-99b8-d207c74cb432",
    "Nice 70.3 - 2024": "04e65ab7-7425-4cdd-80f9-fd10c0ecfb09",
    "Nice 70.3 - 2023": "99f76aa0-8c0f-4638-b4f7-909c0aa300ce",
    "Nice 70.3 - 2022": "5316402b-3702-471e-b02d-a281fd963e42",
    "Swansea 70.3 - 2025": "8b695ceb-5d5a-43de-b6dc-389a836da5fd",
    "Swansea 70.3 - 2024": "cd32f0f7-fb44-4476-b178-05c4fff7bb56",
    "Swansea 70.3 - 2023": "58779cf2-dc52-4b9c-ae92-5156c370b12e",
    "Jonkoping 70.3 - 2025": "3aee4f6b-cc2a-4d7c-8f71-795651d7a3af",
    "Jonkoping 70.3 - 2024": "adb19add-31e8-4076-a995-1e62e7b0c375",
    "Bolton 70.3 - 2025": "963b0ba7-395f-4b06-86cf-ca211e275b53",
    "Bolton 70.3 - 2024": "418c854e-6631-41cf-ba77-7f9a1336b776",
    "Aix-en-Provence 70.3 - 2025": "1d33a788-7afe-4359-b1f3-82fa9fc3ac24",
    "Aix-en-Provence 70.3 - 2024": "4cfda214-447b-4b25-9a07-e323b73ad6b7",
    "Valencia 70.3 - 2025": "a6ba3a9d-c8a6-4cfc-b591-da67e6cf84ca",
    "Valencia 70.3 - 2024": "261f3355-28c7-4677-9c0c-4fccdf4c07e9",
    "Weymouth 70.3 - 2024": "32d50904-af04-4fe7-a5b3-4ffbd19c264f",
    "Weymouth 70.3 - 2023": "21d5f802-e971-4d26-b5f4-e265383a7aa3",
}

age_groups = [
    "All",
    "FPRO",
    "MPRO",
    "M18-24",
    "F18-24",
    "M25-29",
    "F25-29",
    "M30-34",
    "F30-34",
    "M35-39",
    "F35-39",
    "M40-44",
    "F40-44",
    "M45-49",
    "F45-49",
    "M50-54",
    "F50-54",
    "M55-59",
    "F55-59",
    "M60-64",
    "F60-64",
    "M65-69",
    "F65-69",
    "M70-74",
    "F70-74",
]

countries = ["All"]

selected_race = st.sidebar.selectbox("Select Race", list(races.keys()))
selected_age_group = st.sidebar.selectbox("Select Age Group", age_groups, index=0)
selected_country = st.sidebar.selectbox("Select Country", countries)


race_id = races[selected_race]

if st.sidebar.button("Fetch Data"):
    with st.spinner("Fetching race data..."):
        # API call
        url = "https://labs-v2.competitor.com/api/results"
        params = {
            "wtc_eventid": race_id,
            "agegroup": selected_age_group,
            "country": selected_country,
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = pd.DataFrame.from_dict(response.json()["resultsJson"]["value"])

                # Store data in session state
                st.session_state.data = data
                st.session_state.race_name = selected_race
                st.session_state.age_group = selected_age_group
                st.session_state.country = selected_country

                st.sidebar.success(
                    f"Data fetched successfully! {len(data)} results found."
                )
            else:
                st.sidebar.error(
                    f"Failed to fetch data. Status code: {response.status_code}"
                )
        except Exception as e:
            st.sidebar.error(f"Error fetching data: {str(e)}")


if "data" in st.session_state:
    data = st.session_state.data

    st.subheader(
        f"Analysis for {st.session_state.race_name} - {st.session_state.age_group} - {st.session_state.country}"
    )
    if len(data) > 0:
        data["wtc_finisher"] = data["wtc_finisher"].astype(int)
        data_no_dnf = data.drop(data[data.wtc_finisher == 0].index)

        def format_timedelta(td):
            total_seconds = int(td.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                return f"{hours:01}:{minutes:02}:{seconds:02}"
            else:
                return f"{minutes:01}:{seconds:02}"

        if len(data_no_dnf) > 0:
            # Swim
            data_no_dnf["swim_time"] = pd.to_timedelta(
                data_no_dnf["wtc_swimtimeformatted"]
            )
            data_no_dnf["swim_time_minutes"] = (
                data_no_dnf["swim_time"].dt.total_seconds() / 60
            )

            # T1
            data_no_dnf["T1_time"] = pd.to_timedelta(
                data_no_dnf["wtc_transition1time_formatted"]
                .str.replace(",", "")
                .astype(int),
                unit="s",
            )
            data_no_dnf["T1_time_minutes"] = (
                data_no_dnf["T1_time"].dt.total_seconds() / 60
            )

            # Bike
            data_no_dnf["bike_time"] = pd.to_timedelta(
                data_no_dnf["wtc_biketimeformatted"]
            )
            data_no_dnf["bike_time_minutes"] = (
                data_no_dnf["bike_time"].dt.total_seconds() / 60
            )

            # T2
            data_no_dnf["T2_time"] = pd.to_timedelta(
                data_no_dnf["wtc_transition2time_formatted"]
                .str.replace(",", "")
                .astype(int),
                unit="s",
            )
            data_no_dnf["T2_time_minutes"] = (
                data_no_dnf["T2_time"].dt.total_seconds() / 60
            )

            # Run
            data_no_dnf["run_time"] = pd.to_timedelta(
                data_no_dnf["wtc_runtime_formatted"].str.replace(",", "").astype(int),
                unit="s",
            )
            data_no_dnf["run_time_minutes"] = (
                data_no_dnf["run_time"].dt.total_seconds() / 60
            )

            # Finish time
            data_no_dnf["finish_time"] = pd.to_timedelta(
                data_no_dnf["wtc_finishtime_formatted"]
                .str.replace(",", "")
                .astype(int),
                unit="s",
            )
            data_no_dnf["finish_time_minutes"] = (
                data_no_dnf["finish_time"].dt.total_seconds() / 60
            )

        # DNF Analysis
        st.subheader("DNF Analysis")
        col1, col2 = st.columns(2)

        with col1:
            dnf = data.groupby(["wtc_finisher"]).size().reset_index(name="count")
            fig, ax = plt.subplots(figsize=(8, 6))
            labels = ["DNF" if x == 0 else "Finisher" for x in dnf["wtc_finisher"]]
            ax.pie(dnf["count"], labels=labels, autopct="%1.1f%%")
            ax.set_title("DNF vs Finisher Distribution")
            st.pyplot(fig)

        with col2:
            st.metric("Total Participants", len(data))
            st.metric("Finishers", len(data_no_dnf))
            if len(data) > 0:
                dnf_rate = (len(data) - len(data_no_dnf)) / len(data) * 100
                st.metric("DNF Rate", f"{dnf_rate:.1f}%")

        if len(data_no_dnf) > 0:

            def create_histogram(data_col, title, xlabel, time_unit="minutes"):
                if time_unit == "hours":
                    data_col = data_col / 60
                    unit_label = "hours"
                else:
                    unit_label = "minutes"

                mean_time = data_col.mean()
                median_time = data_col.median()

                fig, ax = plt.subplots(figsize=(10, 6))
                counts, bins, patches = ax.hist(
                    data_col, bins=10, color="skyblue", edgecolor="black"
                )
                ax.set_xlabel(f"{xlabel} ({unit_label})")
                ax.set_ylabel("Frequency")
                ax.set_title(f"Histogram of {title} (excluding DNFs)")
                ax.grid(True)

                ax2 = ax.twinx()
                total_count = len(data_col)
                percentages = (counts / total_count) * 100
                ax2.set_ylabel("Percentage (%)", color="blue")
                ax2.set_ylim(0, 110)
                ax2.tick_params(axis="y", labelcolor="blue")

                ax2.plot(
                    bins[:-1],
                    np.cumsum(percentages),
                    color="blue",
                    linewidth=2,
                    label="Cumulative %",
                )

                mean_line = ax.axvline(
                    mean_time,
                    color="red",
                    linestyle="--",
                    linewidth=2,
                    label=f"Mean: {mean_time:.2f} {unit_label}",
                )
                median_line = ax.axvline(
                    median_time,
                    color="green",
                    linestyle="--",
                    linewidth=2,
                    label=f"Median: {median_time:.2f} {unit_label}",
                )

                for b in bins:
                    ax.text(
                        b,
                        max(counts) * 0.02,
                        f"{b:.1f}",
                        rotation=0,
                        va="bottom",
                        ha="center",
                        fontsize=9,
                        color="red",
                    )

                lines, labels = ax.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax.legend(lines + lines2, labels + labels2, loc="center right")
                return fig

            # Swim Analysis
            st.subheader("Swim Times")
            if not data_no_dnf["wtc_swimtimeformatted"].isna().all():
                fig_swim = create_histogram(
                    data_no_dnf["swim_time_minutes"], "Swim Times", "Swim Time"
                )
                st.pyplot(fig_swim)
            else:
                st.error("No swim data in the dataset, this is not a bug !")

            # T1 Analysis
            st.subheader("T1 Times")
            if not data_no_dnf["wtc_transition1time_formatted"].isna().all():
                fig_t1 = create_histogram(
                    data_no_dnf["T1_time_minutes"], "T1 Times", "T1 Time"
                )
                st.pyplot(fig_t1)
            else:
                st.error("No T1 data in the dataset, this is not a bug !")

            # Bike Analysis
            st.subheader("Bike Times")
            if not data_no_dnf["wtc_biketimeformatted"].isna().all():
                fig_bike = create_histogram(
                    data_no_dnf["bike_time_minutes"], "Bike Times", "Bike Time", "hours"
                )
                st.pyplot(fig_bike)
            else:
                st.error("No bike data in the dataset, this is not a bug !")

            # T2 Analysis
            st.subheader("T2 Times")
            if not data_no_dnf["wtc_transition2time_formatted"].isna().all():
                fig_t2 = create_histogram(
                    data_no_dnf["T2_time_minutes"], "T2 Times", "T2 Time"
                )
                st.pyplot(fig_t2)
            else:
                st.error("No T2 data in the dataset, this is not a bug !")

            # Run Analysis
            st.subheader("Run Times")
            if not data_no_dnf["wtc_runtime_formatted"].isna().all():
                fig_run = create_histogram(
                    data_no_dnf["run_time_minutes"], "Run Times", "Run Time", "hours"
                )
                st.pyplot(fig_run)
            else:
                st.error("No run data in the dataset, this is not a bug !")

            # Finish Time Analysis
            st.subheader("Overall Finish Times")
            fig_finish = create_histogram(
                data_no_dnf["finish_time_minutes"],
                "Finish Times",
                "Finish Time",
                "hours",
            )
            st.pyplot(fig_finish)

            # Summary Statistics
            st.subheader("Summary Statistics")
            summary_data = {
                "Discipline": ["Swim", "T1", "Bike", "T2", "Run", "Total"],
                "Mean (min)": [
                    data_no_dnf["swim_time_minutes"].mean(),
                    data_no_dnf["T1_time_minutes"].mean(),
                    data_no_dnf["bike_time_minutes"].mean(),
                    data_no_dnf["T2_time_minutes"].mean(),
                    data_no_dnf["run_time_minutes"].mean(),
                    data_no_dnf["finish_time_minutes"].mean(),
                ],
                "Median (min)": [
                    data_no_dnf["swim_time_minutes"].median(),
                    data_no_dnf["T1_time_minutes"].median(),
                    data_no_dnf["bike_time_minutes"].median(),
                    data_no_dnf["T2_time_minutes"].median(),
                    data_no_dnf["run_time_minutes"].median(),
                    data_no_dnf["finish_time_minutes"].median(),
                ],
            }

            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df)

        else:
            st.warning("No finishers found for the selected criteria.")

    else:
        st.error("No data found, this is not a bug !")


else:
    st.info("Please select race parameters and click 'Fetch Data' to begin analysis.")

st.sidebar.markdown("---")
st.sidebar.markdown("### Instructions")
st.sidebar.markdown("1. Select your desired race, age group, and country")
st.sidebar.markdown("2. Click 'Fetch Data' to retrieve results")
st.sidebar.markdown("3. View the analysis charts and statistics")
st.sidebar.markdown("4. Change parameters and fetch new data as needed")
