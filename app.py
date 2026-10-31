import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date

st.set_page_config(
    page_title="Smart Study Planner",
    page_icon="📚",
    layout="wide"
)
file_path = Path("tasks.json")
hours_file = Path("study_hours.json")
weekly_file = Path("weekly_plan.json")

if hours_file.exists():
    study_hours = json.loads(hours_file.read_text())
else:
    study_hours = {}
    weekly_file = Path("weekly_plan.json")

if weekly_file.exists():
    weekly_plan = json.loads(weekly_file.read_text())
else:
    weekly_plan = []

if "weekly_plan" not in st.session_state:
    st.session_state.weekly_plan = weekly_plan

if "tasks" not in st.session_state:
    if file_path.exists():
        st.session_state.tasks = json.loads(file_path.read_text())
    else:
        st.session_state.tasks = []

page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Study Timetable", "Study Progress"]
)
if page == "Dashboard":
    if page == "Dashboard":
        st.title("📚 Smart Study Planner")

    st.markdown("""
    <div style="
        background: linear-gradient(120deg, #173B67, #3979B9);
        padding: 28px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
    ">
        <h2 style="color:white;">Welcome to Your Study Space! 📚</h2>
        <p style="color:white;">
            Plan smart, study consistently and achieve your goals.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Organize your subjects • Plan your time • Track your progress")
    st.success("Welcome! Let's make today productive.")

    st.markdown(
        "> Success is the sum of small efforts repeated day in and day out."
    )

    tasks = st.session_state.tasks

    total_tasks = len(tasks)
    completed_tasks = sum(
        1 for task in tasks
        if task["Status"] == "Completed"
    )
    pending_tasks = total_tasks - completed_tasks

    total_hours = sum(study_hours.values())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📚 Total Tasks", total_tasks)
    col2.metric("✅ Completed", completed_tasks)
    col3.metric("⏳ Pending", pending_tasks)
    col4.metric("⏰ Study Hours", f"{total_hours:.1f}")

    st.markdown("---")
    st.subheader("📈 Overall Completion")

    if total_tasks > 0:
        percentage = (completed_tasks / total_tasks) * 100
        st.progress(percentage / 100)
        st.write(f"You have completed {percentage:.1f}% of your tasks.")
    else:
        st.info("Add your first study task to track your progress.")

    st.markdown("---")
    st.subheader("📚 Subject-wise Study Summary")

    if tasks:
        subject_data = pd.DataFrame(tasks)
        subject_summary = subject_data.groupby("Subject").size()
        st.bar_chart(subject_summary)
    else:
        st.info("Add tasks to see your subject-wise summary.")

elif page == "Study Timetable":
    st.title("📅 Study Timetable")
    st.write("Your planned study activities")

    if st.session_state.tasks:
        timetable = pd.DataFrame(st.session_state.tasks)
        st.dataframe(timetable, use_container_width=True)
    else:
        st.info("No study tasks added yet. Add tasks in Dashboard.")

    st.markdown("---")
    st.subheader("🗓️ Create Weekly Study Timetable")

    days = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    selected_day = st.selectbox("Select Day", days)
    subject = st.text_input("Enter Subject")
    topic = st.text_input("Enter Topic")
    study_time = st.text_input("Enter Study Time")

    if st.button("Add to Weekly Timetable"):
        if subject and topic and study_time:
            st.session_state.weekly_plan.append({
                "Day": selected_day,
                "Subject": subject,
                "Topic": topic,
                "Study Time": study_time
            })

            weekly_file.write_text(
                json.dumps(st.session_state.weekly_plan, indent=4)
            )
            st.success("Study timetable added successfully!")
        else:
            st.warning("Please fill in all the details.")

    st.markdown("---")
    st.subheader("📚 Your Weekly Timetable")

    if st.session_state.weekly_plan:
        for i, item in enumerate(st.session_state.weekly_plan):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(
                    f"{item['Day']} | {item['Subject']} | "
                    f"{item['Topic']} | {item['Study Time']}"
                )

            with col2:
                if st.button("🗑️ Delete", key=f"delete_weekly_{i}"):
                    st.session_state.weekly_plan.pop(i)

                    weekly_file.write_text(
                        json.dumps(st.session_state.weekly_plan, indent=4)
                    )
                    st.rerun()
    else:
        st.info("No weekly timetable entries added yet.")

elif page == "Study Progress":
    tasks = st.session_state.tasks
    total = len(tasks)
    completed = sum(1 for task in tasks if task["Status"] == "Completed")
    remaining = total - completed
    st.subheader("📊 Progress Graph")

    chart_data = pd.DataFrame({
        "Status": ["Completed", "Remaining"],
        "Tasks": [completed, remaining]
    })

    st.bar_chart(chart_data.set_index("Status"))
    st.markdown("---")
    st.subheader("🎯 Daily Study Goal")

    daily_goal = st.number_input(
        "Set your daily study target (hours)",
        min_value=1,
        max_value=12,
        value=4
    )

    st.write(f"Your daily study goal is {daily_goal} hours.")
    st.markdown("---")
    st.subheader("⏱️ Record Your Study Hours")

    actual_hours = st.number_input(
        "How many hours did you study today?",
        min_value=0.0,
        max_value=24.0,
        value=0.0,
        step=0.5
    )

    st.write(f"Today's study hours: {actual_hours} hours")
    today = str(date.today())
    study_hours[today] = actual_hours

    hours_file.write_text(json.dumps(study_hours, indent=4))
    st.subheader("📅 Study History")

    history = pd.DataFrame(
        list(study_hours.items()),
        columns=["Date", "Hours Studied"]
    )

    st.dataframe(history, use_container_width=True)

    if actual_hours >= daily_goal:
        st.success("🎉 Daily study goal achieved!")
    else:
        st.info(f"You need {daily_goal - actual_hours:.1f} more hours to reach your goal.")
    st.title("📊 Study Progress")
    st.markdown("---")
    st.subheader("📥 Download Study Report")

    if st.session_state.tasks:
        report = pd.DataFrame(st.session_state.tasks)

        csv = report.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Report",
            data=csv,
            file_name="My_Study_Report.csv",
            mime="text/csv"
        )
    else:
        st.info("No study tasks available to download.")

st.markdown("""
<style>
.stApp {
    background-color: #F4F7FC;
    color: #263445;
}

.stApp p, .stApp label {
    color: #263445 !important;
}

h1, h2, h3 {
    color: #173B67 !important;
}

section[data-testid="stSidebar"] {
    background-color: #E3ECF8;
}

.stButton button {
    background-color: #24558A;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)
st.sidebar.title("📚 Study Planner")
st.sidebar.write("Welcome!")
st.sidebar.markdown("---")
st.sidebar.info("Plan your study time and track your progress.")

total_tasks = len(st.session_state.tasks)

completed_tasks = sum(
    1 for task in st.session_state.tasks
    if task["Status"] == "Completed"
)

remaining_tasks = total_tasks - completed_tasks

col1, col2, col3 = st.columns(3)

col1.metric("📚 Total Tasks", total_tasks)
col2.metric("✅ Completed", completed_tasks)
col3.metric("⏳ Remaining", remaining_tasks)
st.write("Plan your studies and manage your time!")

st.subheader("Add a Study Task")

subject = st.text_input("Enter subject name")
topic = st.text_input("Enter topic to study")
hours = st.number_input("Study hours", min_value=1, max_value=12, value=2)

if "tasks" not in st.session_state:
    file = Path("tasks.json")

    if file.exists():
        st.session_state.tasks = json.loads(
            file.read_text(encoding="utf-8")
        )
    else:
        st.session_state.tasks = []

if st.button("Add Task"):
    if subject.strip() and topic.strip():
        st.session_state.tasks.append({
            "Subject": subject,
            "Topic": topic,
            "Hours": hours,
            "Status": "Not Completed"
        })
        file_path.write_text(json.dumps(st.session_state.tasks, indent=4))
        st.success("Task added successfully!")
    else:
        st.warning("Please enter both subject and topic.")

st.subheader("My Study Schedule")
if st.session_state.tasks:
    for i, task in enumerate(st.session_state.tasks):
        st.write(f"**{task['Subject']}** - {task['Topic']}")
        st.write(f"Study hours: {task['Hours']}")

        col1, col2 = st.columns([4, 1])

        with col1:
            completed = st.checkbox(
                "Completed",
                value=(task["Status"] == "Completed"),
                key=f"task_{i}"
            )

            if completed:
                task["Status"] = "Completed"
            else:
                task["Status"] = "Not Completed"
        file_path.write_text(json.dumps(st.session_state.tasks, indent=4))

        with col2:
            if st.button("🗑️ Delete", key=f"delete_{i}"):
                st.session_state.tasks.pop(i)
                file_path.write_text(json.dumps(st.session_state.tasks, indent=4))
                st.rerun()

else:
    st.info("No study tasks added yet.")

st.write("Small steps every day lead to big achievements!")

st.subheader("📈 Study Progress")

if st.session_state.tasks:
    completed = sum(
        1 for task in st.session_state.tasks
        if task["Status"] == "Completed"
    )
    total = len(st.session_state.tasks)
    progress = completed / total

    st.progress(progress)
    st.write(f"Completed: {completed} out of {total} tasks")
else:
    st.info("Add a study task to track your progress.")