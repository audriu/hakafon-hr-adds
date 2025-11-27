# GitHub Copilot Instructions

## Python Environment

This project uses a Python virtual environment located at `.venv/`.

**Important**: Before running any Python commands in the terminal, always activate the virtual environment first:

```bash
source .venv/bin/activate
```

## Command Line Execution Rules

When suggesting or executing Python commands in the terminal:

1. **Always activate the virtual environment first** using `source .venv/bin/activate`
2. Then run the Python command
3. You can chain commands using `&&`, for example:
   ```bash
   source .venv/bin/activate && python main.py
   ```

## Examples

**Running the main script:**
```bash
source .venv/bin/activate && python main.py
```

**Running tests:**
```bash
source .venv/bin/activate && pytest test_scraper.py
```

**Installing dependencies:**
```bash
source .venv/bin/activate && pip install -r requirements.txt
```

**Installing packages with uv:**
```bash
source .venv/bin/activate && uv pip install <package-name>
```
