# Examples

This directory contains usage examples for the SEIZ epidemic models package.

## Basic Usage Example

Run the basic usage example to see all three models in action:

```bash
cd examples
python3 basic_usage.py
```

Or from the repository root:

```bash
python3 examples/basic_usage.py
```

This will:
1. Run the basic SEIZ model
2. Run the SEIZ-BM (Basic Moderator) model
3. Run the SEIZ-SM (Smart Moderator) model
4. Generate JSON output files for each model
5. Create a comparison visualization (`model_comparison.png`)

## Output Files

The example generates:
- `seiz_basic_results.json` - Results from basic SEIZ model
- `seiz_bm_results.json` - Results from SEIZ-BM model
- `seiz_sm_results.json` - Results from SEIZ-SM model
- `model_comparison.png` - Visual comparison of all three models

Note: These output files are excluded from version control.
