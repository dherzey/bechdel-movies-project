#---------------------------------------------------------------------------
# This could be used for first time running of ETL scripts or for resetting 
# of ETL configs. This include Bash commands to run all scripts and commands 
# needed for this project's ETL process. Make sure that all packages found 
# in requirement.txt are installed.
#
# NOTE: To make this file executable, please run the following command:
#         chmod +x run_project.sh
# EXECUTE this file by typing: source ./run_project.sh
#
# Last modified: April 2023
#--------------------------------------------------------------------------

# create virtual environment
python3 -m venv project-venv
echo "Virtual environment created."

# activate virtual environment
source ./project-venv/bin/activate
echo "Virtual environment activated."

# pip install Python packages in environment
pip install -r requirements.txt
echo "Required packages installed."

# create blocks
python3 etl/create_prefect_blocks.py
echo "Prefect blocks created."

# create deployments
python3 etl/create_prefect_deployments.py
echo "Prefect deployments created."