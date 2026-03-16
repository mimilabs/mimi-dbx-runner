import os
import sys

from dotenv import load_dotenv


class Config:
    def __init__(self, cluster_id=None, upload_path=None):
        load_dotenv()

        self.host = os.environ.get("DATABRICKS_HOST", "")
        self.token = os.environ.get("DATABRICKS_TOKEN", "")
        self.cluster_id = cluster_id or os.environ.get("DATABRICKS_CLUSTER_ID", "")
        self.upload_path = upload_path or os.environ.get(
            "DBX_UPLOAD_PATH", "/tmp/dbx_runner"
        )

    def validate(self):
        missing = []
        if not self.host:
            missing.append("DATABRICKS_HOST")
        if not self.token:
            missing.append("DATABRICKS_TOKEN")
        if not self.cluster_id:
            missing.append("DATABRICKS_CLUSTER_ID")
        if missing:
            print(f"Error: missing required config: {', '.join(missing)}", file=sys.stderr)
            print("Set them in .env or as environment variables.", file=sys.stderr)
            sys.exit(1)
