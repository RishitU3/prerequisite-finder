# ==============================================================================
# File: chatbot.py (Updated)
#
# This script is an interactive chatbot that uses the course data generated
# by `scraper.py` to answer user queries about course prerequisites.
# It now includes a command to list all available courses.
# ==============================================================================

import json
import os

# Define the path to the data file.
DATA_FILE = os.path.join("data", "prereqs.json")


def load_data():
    """
    Loads the course data from the JSON file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a course.
    """
    if not os.path.exists(DATA_FILE):
        print(f"Error: Data file not found at {DATA_FILE}")
        print("Please run scraper.py first to generate the data.")
        return None

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def list_all_courses(data):
    """
    Prints a formatted list of all course titles and their sources.

    Args:
        data (list): The list of course dictionaries.
    """
    print("\n--- Available Courses ---")
    if not data:
        print("No courses found in the database.")
        return

    for course in data:
        title = course.get("title", "Unknown Title")
        source = course.get("source", "Unknown Source")
        print(f"- {title} (Source: {source})")
    print("-------------------------")


def find_prerequisites(course_name, data):
    """
    Finds the prerequisites for a given course name.

    Args:
        course_name (str): The name of the course to look up.
        data (list): The list of course dictionaries.

    Returns:
        str: A formatted string of prerequisites or a "not found" message.
    """
    for course in data:
        # Check for case-insensitive matches
        if course["title"].lower() == course_name.lower():
            prereqs = course.get("prerequisites", "Not specified")
            source = course.get("source", "Unknown")
            return f"The prerequisites for '{course['title']}' are: {prereqs}. (Source: {source})"

    return f"Sorry, I could not find a course named '{course_name}' in the database."


def run_chatbot():
    """
    Runs the main chatbot loop.
    """
    print("Loading course data...")
    course_data = load_data()

    if not course_data:
        return

    print("Data loaded successfully. Ask me about course prerequisites!")
    print("You can also type 'list' to see all available courses or 'exit' to end the session.")

    while True:
        user_input = input("\nEnter a course name or command: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        elif user_input.lower() == "list":
            list_all_courses(course_data)
        elif not user_input:
            print("Please enter a course name or command.")
            continue
        else:
            # Call the function to find the prerequisites
            response = find_prerequisites(user_input, course_data)
            print(response)


# Run the chatbot if the script is executed directly
if __name__ == "__main__":
    run_chatbot()
