from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__, static_folder="static")
CORS(app)

# 🔥 Absolute file path for CSV file (ensure this is correct)
CSV_FILE = os.path.join(os.path.dirname(__file__), "stackoverflow_tags_selected_2023-2025.csv")

# 🔥 Print the CSV file path to check where it's looking for the file
print(f"Looking for CSV file at: {CSV_FILE}")

# 🔥 Check if the file exists
if not os.path.exists(CSV_FILE):
    print(" CSV file not found!")
else:
    print(" CSV file found!")

# 🎨 Fixed colors for tags
TAG_COLORS = {
    "python": "#377eb8", "java": "#ff7f00", "javascript": "#4daf4a", 
    "c++": "#984ea3", "c#": "#e41a1c", "html": "#f781bf", 
    "css": "#a65628", "react": "#fdae61", "angular": "#66c2a5", 
    "flutter": "#d73027"
}

@app.route('/data', methods=['GET'])
def get_json_data():
    """Return JSON data of tag trends."""
    try:
        if not os.path.exists(CSV_FILE):
            return jsonify({"error": "CSV file not found!"}), 404

        # Read CSV file with pandas and parse the 'Time' column as datetime
        df = pd.read_csv(CSV_FILE, encoding="utf-8")
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")  # Handle invalid dates
        df["Year"] = df["Time"].dt.year  # Extract year from the 'Time' column
        df = df.dropna(subset=["Year"])  # Drop rows where 'Year' is NaN

        # Group by 'Year' and 'Tag', and calculate the count of each tag per year
        tag_counts = df.groupby(["Year", "Tag"]).size().reset_index(name="Count")
        total_tags_per_year = tag_counts.groupby("Year")["Count"].transform("sum")
        tag_counts["Normalized_Count"] = (tag_counts["Count"] / total_tags_per_year) * 100  # Normalize count to %

        # Get the top 10 tags based on normalized count
        top_tags = tag_counts.groupby("Tag")["Normalized_Count"].sum().nlargest(10).index.tolist()
        tag_counts = tag_counts[tag_counts["Tag"].isin(top_tags)]

        # Prepare data for each tag to return in the response
        result = {}
        for tag in top_tags:
            tag_data = tag_counts[tag_counts["Tag"] == tag][["Year", "Normalized_Count"]].to_dict(orient="records")
            result[tag] = tag_data

        return jsonify(result)

    except Exception as e:
        # Print error message for debugging purposes
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/index.html')
def serve_data_html():
    """Serve the index.html page from the static folder."""
    return send_from_directory("static", "index.html")


if __name__ == '__main__':
    # Run the app in debug mode (use debug=False in production)
    app.run(debug=True)
