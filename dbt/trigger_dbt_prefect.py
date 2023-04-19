"""----------------------------------------------------------------------
Python script which uses Prefect to trigger dbt flows. The trigger_dbt()
function is also a Prefect task which will be called in a flow under
the create_prefect_deployments.py script.

Last modified: April 2023
----------------------------------------------------------------------"""

from prefect import task
from prefect_dbt.cli.commands import DbtCoreOperation


@task(log_prints=True)
def trigger_dbt(target, is_test):
    """
    Create a flow to trigger dbt commands. This uses the 
    profiles under the dbt folder.

    Arguments:
        - target: the name of the target profile to use. 
                  Can either be dev or prod.
        - is_test: accepts boolean. If False, dbt will give full results
                   of models. Otherwise, results are limited to 1000.

    Returns:
        None
    """

    result = DbtCoreOperation(
            project_dir = "./dbt/",
            profiles_dir = "./dbt/",
            commands = [f"dbt run --target {target} \
                        --vars {{is_test:{is_test}}}"]
    )

    result.run()