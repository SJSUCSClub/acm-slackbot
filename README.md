# ACM Slackbot

General purpose slackbot for automating officer workflows.

## Running Locally

### 1. Slack Setup

To get started, you should first create a Slack account and your own (free) Slack workspace
to test this app in.

Once you have a workspace, follow the instructions from [Getting Started with Bolt for Python](https://docs.slack.dev/tools/bolt-python/getting-started/#running-the-app)
to create the app and add it to your workspace

### 2. Environment Setup

To run this app locally, you'll need to create a `.env` file with the following values
in the root directory of this project:

```bash
SLACK_BOT_TOKEN=<your-bot-token>
SLACK_APP_TOKEN=<your-app-level-token>
```

Then, you'll also want to create a virtual environment and install the dependencies by running
the following commands in your terminal:

```bash
uv venv .venv --python=3.14
source .venv/bin/activate
pip install -r requirements.txt
```

> If you don't have uv, you can install it by following [these instructions](https://docs.astral.sh/uv/getting-started/installation/)
> Or, you could use an alternative virtual environment manager. For example, `python3 -m venv .venv`

### 3. Start servers

Now that you have your environment set up, you can start the app by running the following command:

```zsh
python3 app.py
```

To stop the app, press `CTRL+C` (or `Command+C` on a Mac) in your terminal.

## Project Structure

The project is structured as follows:

```bash
.
├── app.py
├── handlers
│   ├── __init__.py
│   └── misc.py
├── requirements.txt
└── README.md
```

All the files in the `handlers` directory should contain event handlers for the app. To add a new
file, create a new file in the `handlers` directory and add the event handlers to it. Make sure to
define a function called `register(app: App)` in the file (see `handlers/misc.py`) and call that
`register` function in the `app.py` file.

## More examples

Looking for more examples of Bolt for Python? Browse to [bolt-python/examples/](https://github.com/slackapi/bolt-python/tree/main/examples) for a long list of usage, server, and deployment code samples!
