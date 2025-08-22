# ==============================================================================
# File: process_courses.py
#
# This script reads course data from a CSV file, processes it, and
# provides a structured JSON output.
#
# It is designed to work with the specific column names provided by the user.
# The script will now handle: Department, Course Code, Course Title,
# Faculty Incharge, Except For, Swayam_URL, and Prerequisites.
# ==============================================================================

import pandas as pd
import json
import os
import re


def process_course_data(input_csv_path, output_json_path):
    """
    Reads a CSV file containing course data, processes it to a structured
    format, and saves the result as a JSON file.

    Args:
        input_csv_path (str): The path to the input CSV file.
        output_json_path (str): The path where the processed JSON will be saved.
    """
    if not os.path.exists(input_csv_path):
        print(f"Error: The file '{input_csv_path}' was not found.")
        print("Please make sure the CSV file is in the same folder as this script.")
        return

    try:
        # Read the CSV file into a pandas DataFrame.
        # We now use the column names provided by the user.
        # The 'errors' parameter is added to skip bad lines.
        df = pd.read_csv(input_csv_path, encoding='utf-8', on_bad_lines='skip')

        # Check if the required columns exist
        required_columns = ['Department', 'Course Code', 'Course Title', 'Faculty Incharge', 'Except For', 'Swayam_URL',
                            'Prerequisites']
        if not all(col in df.columns for col in required_columns):
            print("Error: The CSV file must contain the following columns:")
            print(", ".join(required_columns))
            return

        # Create a list to hold the processed course data
        processed_courses = []

        # Iterate over each row in the DataFrame to process the data
        for index, row in df.iterrows():
            department = str(row['Department']).strip()
            course_code = str(row['Course Code']).strip()
            course_title = str(row['Course Title']).strip()
            faculty_incharge = str(row['Faculty Incharge']).strip()
            except_for = str(row['Except For']).strip()
            swayam_url = str(row['Swayam_URL']).strip()
            prerequisites_raw = str(row['Prerequisites']).strip()

            # Combine relevant fields to create a rich description
            description = f"{course_title}. Except For: {except_for}."

            # Split the prerequisites string into a list of individual courses.
            # We'll handle different separators like commas, semicolons, or "and".
            prerequisites = []
            if prerequisites_raw.lower() != 'nan':
                prereq_list = re.split(r'[,;]\s*| and ', prerequisites_raw)
                prerequisites = [p.strip() for p in prereq_list if p.strip()]

            # Create a dictionary for the current course
            course_data = {
                "department": department,
                "course_code": course_code,
                "course_name": course_title,
                "description": description,
                "faculty_incharge": faculty_incharge,
                "swayam_url": swayam_url,
                "prerequisites": prerequisites
            }

            processed_courses.append(course_data)

        # Save the processed data to a JSON file for easy use in other applications
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(processed_courses, f, indent=4)

        print("\nProcessing complete! 🎉")
        print(f"Successfully processed {len(processed_courses)} courses.")
        print(f"Data saved to '{output_json_path}'.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Define the input and output file paths
    input_file = "courses.csv"
    output_file = "processed_courses.json"

    # Run the main processing function
    process_course_data(input_file, output_file)
