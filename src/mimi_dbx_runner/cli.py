import argparse
import sys

from mimi_dbx_runner.config import Config
from mimi_dbx_runner.client import DatabricksRunner


def parse_param(value):
    if "=" not in value:
        print(f"Error: invalid param format '{value}', expected KEY=VALUE", file=sys.stderr)
        sys.exit(1)
    key, val = value.split("=", 1)
    return key, val


def main():
    parser = argparse.ArgumentParser(
        prog="dbx-run",
        description="Run a Databricks notebook from your local repo",
    )
    parser.add_argument("notebook", help="Path to local notebook (.py or .ipynb)")
    parser.add_argument(
        "-p", "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Widget parameter (repeatable)",
    )
    parser.add_argument("--cluster-id", help="Override DATABRICKS_CLUSTER_ID")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep uploaded notebook in workspace")
    parser.add_argument("--upload-path", help="Override DBX_UPLOAD_PATH")

    args = parser.parse_args()

    params = dict(parse_param(p) for p in args.param)

    config = Config(cluster_id=args.cluster_id, upload_path=args.upload_path)
    config.validate()

    runner = DatabricksRunner(config)
    runner.run(args.notebook, params=params, cleanup=not args.no_cleanup)
