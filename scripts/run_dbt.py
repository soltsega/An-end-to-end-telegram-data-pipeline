import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_dbt():
    # Get arguments passed to the script (e.g., debug, run, test)
    dbt_args = sys.argv[1:]
    
    if not dbt_args:
        print("Please provide a dbt command (e.g., debug, run).")
        return

    # Path to dbt executable in the virtual environment
    # Assuming the script is run from the project root
    dbt_path = os.path.join("venv", "Scripts", "dbt")
    
    if not os.path.exists(dbt_path + ".exe"): # Windows check
        # Fallback if checking plain 'dbt'
        if not os.path.exists(dbt_path):   
            print(f"Error: dbt executable not found at {dbt_path}")
            return

    # Construct the full command
    command = [dbt_path] + dbt_args
    
    print(f"Running dbt command: {' '.join(command)}")
    
    # Run the command with the loaded environment variables
    # We must ensure we are in the dbt project directory (medical_warehouse)
    project_dir = "medical_warehouse"
    if not os.path.exists(project_dir):
        print(f"Error: dbt project directory '{project_dir}' not found.")
        return

    try:
        subprocess.run(command, cwd=project_dir, env=os.environ, check=True)
    except subprocess.CalledProcessError as e:
        print(f"dbt command failed with exit code {e.returncode}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_dbt()
