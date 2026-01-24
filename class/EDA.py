import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# Step 1: Create Dataset
# -------------------------------
df = pd.DataFrame({
    "Age": [16, 17, 18, 19, 21, 25, 30, 40, 50],
    "Gender": ["Male", "Female", "Female", "Male", "Male", "Female", "Female", "Male", "Female"],
    "Marks": [85, 78, 82, 90, 75, 88, 95, 70, 60]
})

print("\n--- Dataset ---")
print(df)

# -------------------------------
# Step 2: Numerical vs Numerical
# Age vs Marks
# -------------------------------
print("\n--- Numerical vs Numerical (Correlation) ---")
print(df[["Age", "Marks"]].corr())

plt.scatter(df["Age"], df["Marks"])
plt.xlabel("Age")
plt.ylabel("Marks")
plt.title("Age vs Marks")
plt.show()

# -------------------------------
# Step 3: Categorical vs Numerical
# Gender vs Marks
# -------------------------------
print("\n--- Categorical vs Numerical (Average Marks by Gender) ---")
print(df.groupby("Gender")["Marks"].mean())

df.boxplot(column="Marks", by="Gender")
plt.title("Marks Distribution by Gender")
plt.suptitle("")
plt.show()

# -------------------------------
# Step 4: Categorical vs Categorical
# Gender vs Pass/Fail
# -------------------------------
df["Pass"] = df["Marks"] >= 40

print("\n--- Categorical vs Categorical (Gender vs Pass) ---")
print(pd.crosstab(df["Gender"], df["Pass"]))