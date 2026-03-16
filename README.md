# mimi-dbx-runner

CLI tool to run Databricks notebooks from local git repos.

## Install

```bash
pip install -e /path/to/mimi-dbx-runner
```

## Setup

Create a `.env` in your project directory (see `.env.example`):

```
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi...
DATABRICKS_CLUSTER_ID=xxxx-xxxxxx-xxxxxxxx
DBX_UPLOAD_PATH=/Users/your.email@company.com/dbx_runner_tmp
```

## Usage

```bash
dbx-run <notebook_path> [options]

Options:
  -p, --param KEY=VALUE    Widget parameter (repeatable)
  --cluster-id ID          Override DATABRICKS_CLUSTER_ID
  --no-cleanup             Keep uploaded notebook in workspace
  --upload-path PATH       Override DBX_UPLOAD_PATH
```

### Examples

```bash
dbx-run my_notebook.py -p client_name=acme
dbx-run analysis.ipynb -p start_date=2024-01-01 --no-cleanup
python -m mimi_dbx_runner notebook.py -p key=value
```
