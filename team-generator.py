import random

# Candidate list
candidates = [
    "Abitej Budidha",
    "Akhila Shaik",
    "Akshaya Arepalli",
    "Praveena Bontula",
    "Vaishnavi Gajula",
    "Ganavi Durga Lakshmi Tejaswini Perumahanthi",
    "Likhitha Gannina",
    "Kavya Gembali",
    "Keerthikadevi Killi",
    "Kiran Mani Sri Sushma Pulagam",
    "Krishna Meghana Katta",
    "Lakshmi Lakkaraju",
    "Lavanya Yerrareddy",
    "Likitha Mandula",
    "Sireesha Mekala",
    "Mithilesh Giradkar",
    "Mounika Chintalapati",
    "Naresh Pampari",
    "Hema Sai Nunna",
    "Geya Geeta Sree Padmanabhuni",
    "Surya Sai Basheeranjali Patneedi",
    "Veena Pillalamarri",
    "Laya Samyuktha Podishetty",
    "Poojitha Vuyyuri",
    "Rashmi Sahoo",
    "Sadiya Almas Shaik",
    "Saimani Sirangi",
    "Suryaprakash Kandula",
    "Swarnalatha Kada",
    "Thirupathi Reddy Picharla",
    "Vyshnavi Panchumarthi"
]

GROUP_SIZE = 3

# Optional: Set a seed for reproducible results
# random.seed(42)

# Shuffle candidates randomly
random.shuffle(candidates)

# Create groups of 3
groups = [
    candidates[i:i + GROUP_SIZE]
    for i in range(0, len(candidates), GROUP_SIZE)
]

# If the last group has fewer than 3 members,
# merge it into the previous group
if len(groups) > 1 and len(groups[-1]) < GROUP_SIZE:
    groups[-2].extend(groups[-1])
    groups.pop()

# Print groups
for idx, group in enumerate(groups, start=1):
    print(f"\nGroup {idx} ({len(group)} members)")
    print("-" * 40)
    for member in group:
        print(member)