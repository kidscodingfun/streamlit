import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("marksheet.csv")
    return df

df = load_data()

# Sidebar filters
sections = ["All"] + sorted(df["Section"].unique().tolist())
genders = ["All"] + sorted(df["Gender"].unique().tolist())

selected_section = st.sidebar.selectbox("Select Section", sections)
selected_gender = st.sidebar.selectbox("Select Gender", genders)

filtered_df = df.copy()
if selected_section != "All":
    filtered_df = filtered_df[filtered_df["Section"] == selected_section]
if selected_gender != "All":
    filtered_df = filtered_df[filtered_df["Gender"] == selected_gender]

# Sidebar: student selection
student_names = filtered_df["Name"].tolist()
selected_student = st.sidebar.selectbox("Choose a student", student_names)

# Title
st.title("📚 Student Performance Analyzer")

# KPIs
st.subheader("Class Overview")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Students", len(filtered_df))
col2.metric("Avg Age", f"{filtered_df['Age'].mean():.1f}")
col3.metric("Avg Science", f"{filtered_df['Science'].mean():.1f}")
col4.metric("Avg English", f"{filtered_df['English'].mean():.1f}")
col5.metric("Avg Maths", f"{filtered_df['Maths'].mean():.1f}")
col6.metric("Avg History", f"{filtered_df['History'].mean():.1f}")

# Bar chart: average marks per subject
st.subheader("📊 Average Marks per Subject")
avg_marks = filtered_df[["Science","English","History","Maths"]].mean()
plt.figure(figsize=(6,4))
avg_marks.plot(kind="bar", color=["#1f77b4","#ff7f0e","#2ca02c","#d62728"])
plt.ylabel("Average Score")
plt.title("Class Average Marks")
st.pyplot(plt)

# Marks distribution
# Subject colors for consistency
subject_colors = {
    "Science": "#1f77b4",   # blue
    "English": "#ff7f0e",   # orange
    "History": "#2ca02c",   # green
    "Maths": "#d62728"      # red
}

# Sidebar: subject selection for histogram
subjects = ["Science", "English", "History", "Maths"]
selected_subject = st.sidebar.selectbox("Select subject for marks distribution", subjects)

# Marks distribution (subject-specific)
st.subheader(f"📈 Marks Distribution for {selected_subject}")
plt.figure(figsize=(6,4))
filtered_df[selected_subject].plot(
    kind="hist",
    bins=10,
    alpha=0.7,
    color=subject_colors[selected_subject],   # <-- Consistent colors
    edgecolor="black"
)
plt.xlabel("Marks")
plt.ylabel("Number of Students")
plt.title(f"Distribution of {selected_subject} Marks")
st.pyplot(plt)


# --- Student Report Card ---
st.subheader(f"🧑‍🎓 Report Card: {selected_student}")

student_row = filtered_df[filtered_df["Name"] == selected_student].iloc[0]
student_scores = student_row[["Science","English","History","Maths"]]
class_avg = filtered_df[["Science","English","History","Maths"]].mean()

# Student stats
total_marks = student_scores.sum()
avg_marks_student = student_scores.mean()
best_subject = student_scores.idxmax()
worst_subject = student_scores.idxmin()

# Rank within filtered class
filtered_df["TotalMarks"] = filtered_df[["Science","English","History","Maths"]].sum(axis=1)
filtered_df["Rank"] = filtered_df["TotalMarks"].rank(method="min", ascending=False)
student_rank = int(filtered_df.loc[filtered_df["Name"] == selected_student, "Rank"].iloc[0])

# Report Card Metrics
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Marks", int(total_marks))
col2.metric("Average Marks", f"{avg_marks_student:.1f}")
col3.metric("Best Subject", best_subject)
col4.metric("Weakest Subject", worst_subject)
col5.metric("Class Rank", student_rank)

# Comparison chart
st.markdown("### 📊 Performance vs Class Average")
x = range(len(student_scores))
plt.figure(figsize=(6,4))
plt.bar([i-0.2 for i in x], student_scores, width=0.4, label=selected_student)
plt.bar([i+0.2 for i in x], class_avg, width=0.4, label="Class Avg")
plt.xticks(x, ["Science","English","History","Maths"])
plt.ylabel("Marks")
plt.legend()
plt.title(f"{selected_student} vs Class Average")
st.pyplot(plt)

# Show data table
st.subheader("📋 Student Records")
st.dataframe(filtered_df.drop(columns=["TotalMarks", "Rank"]))
