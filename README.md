# stackdiff

> CLI tool to compare deployed vs local environment configs across staging and prod

---

## Installation

```bash
pip install stackdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/stackdiff.git && cd stackdiff && pip install -e .
```

---

## Usage

```bash
stackdiff [OPTIONS] <environment>
```

**Compare local config against staging:**

```bash
stackdiff --local .env.staging --remote staging
```

**Compare staging vs production:**

```bash
stackdiff --diff staging prod
```

**Example output:**

```
[+] DB_HOST         missing in staging
[~] API_TIMEOUT     local=30  deployed=60
[-] LEGACY_FLAG     not in local config
```

### Options

| Flag | Description |
|------|-------------|
| `--local` | Path to local config file |
| `--remote` | Target environment (staging, prod) |
| `--diff` | Compare two deployed environments |
| `--output` | Output format: `table`, `json`, `plain` |

---

## Requirements

- Python 3.8+
- AWS CLI or configured cloud credentials (if pulling remote configs)

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

[MIT](LICENSE)