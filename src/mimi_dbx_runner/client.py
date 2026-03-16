import os
import sys
import time

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import NotebookTask, SubmitTask
from databricks.sdk.service.workspace import ImportFormat, Language


class DatabricksRunner:
    def __init__(self, config):
        self.config = config
        self.client = WorkspaceClient(
            host=config.host,
            token=config.token,
        )
        self._remote_path = None

    def run(self, notebook_path, params=None, cleanup=True):
        try:
            self._upload(notebook_path)
            run_id = self._submit(params or {})
            final_state = self._poll(run_id)
            self._show_output(run_id, final_state)
        finally:
            if cleanup and self._remote_path:
                self._cleanup()

    def _detect_format(self, path):
        if path.endswith(".ipynb"):
            return ImportFormat.JUPYTER, None
        return ImportFormat.SOURCE, Language.PYTHON

    def _upload(self, notebook_path):
        if not os.path.isfile(notebook_path):
            print(f"Error: file not found: {notebook_path}", file=sys.stderr)
            sys.exit(1)

        fmt, language = self._detect_format(notebook_path)
        basename = os.path.splitext(os.path.basename(notebook_path))[0]
        self._remote_path = f"{self.config.upload_path}/{basename}"

        with open(notebook_path, "rb") as f:
            content = f.read()

        import base64

        self.client.workspace.import_(
            path=self._remote_path,
            content=base64.b64encode(content).decode("ascii"),
            format=fmt,
            language=language,
            overwrite=True,
        )
        print(f"Uploaded → {self._remote_path}")

    def _submit(self, params):
        task_kwargs = dict(
            task_key="dbx_run",
            notebook_task=NotebookTask(
                notebook_path=self._remote_path,
                base_parameters=params,
            ),
        )
        if self.config.cluster_id:
            task_kwargs["existing_cluster_id"] = self.config.cluster_id
        else:
            print("Using serverless compute")

        task = SubmitTask(**task_kwargs)
        response = self.client.jobs.submit(
            run_name=f"dbx-run: {os.path.basename(self._remote_path)}",
            tasks=[task],
        )
        print(f"Submitted run {response.run_id}")
        return response.run_id

    def _poll(self, run_id):
        interval = 5
        max_interval = 30
        while True:
            run = self.client.jobs.get_run(run_id)
            state = run.state
            life_cycle = state.life_cycle_state.value if state.life_cycle_state else "UNKNOWN"

            if life_cycle in ("TERMINATED", "SKIPPED", "INTERNAL_ERROR"):
                result = state.result_state.value if state.result_state else "UNKNOWN"
                print(f"Run finished: {life_cycle} / {result}")
                return state

            print(f"  Status: {life_cycle}…", end="\r")
            time.sleep(interval)
            interval = min(interval + 5, max_interval)

    def _show_output(self, run_id, state):
        result = state.result_state.value if state.result_state else "UNKNOWN"

        if result == "SUCCESS":
            try:
                output = self.client.jobs.get_run_output(run_id)
                if output.notebook_output and output.notebook_output.result:
                    print(f"\nNotebook output:\n{output.notebook_output.result}")
            except Exception:
                pass
            print("\nRun succeeded.")
        else:
            message = state.state_message or "No details available."
            print(f"\nRun failed ({result}): {message}", file=sys.stderr)
            sys.exit(1)

    def _cleanup(self):
        try:
            self.client.workspace.delete(self._remote_path)
            print(f"Cleaned up {self._remote_path}")
        except Exception as e:
            print(f"Warning: cleanup failed: {e}", file=sys.stderr)
