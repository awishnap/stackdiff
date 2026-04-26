"""differ_matrix.py — compute a pairwise diff matrix across multiple configs.

Useful when comparing more than two environments at once (e.g. dev, staging,
prod, canary).  The result is a dict-of-dicts keyed by (left_name, right_name)
where each value is a DiffResult from the core differ.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from stackdiff.differ import DiffResult, diff_configs


class MatrixError(Exception):
    """Raised when the matrix cannot be computed."""


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

# Mapping of environment name -> flat config dict
ConfigMap = Dict[str, Dict[str, str]]

# Mapping of (left, right) pair -> DiffResult
DiffMatrix = Dict[Tuple[str, str], DiffResult]


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def build_matrix(
    configs: ConfigMap,
    *,
    symmetric: bool = False,
) -> DiffMatrix:
    """Compute pairwise diffs for every ordered pair of named configs.

    Args:
        configs:   Mapping of environment name to config dict.
        symmetric: When *False* (default) only the upper triangle is computed
                   (i.e. each unique pair once, left < right alphabetically).
                   When *True* both (A, B) and (B, A) are included.

    Returns:
        A dict whose keys are (left_name, right_name) tuples and whose values
        are :class:`~stackdiff.differ.DiffResult` instances.

    Raises:
        MatrixError: If fewer than two configs are provided.
    """
    if len(configs) < 2:
        raise MatrixError(
            f"At least 2 configs are required to build a matrix; got {len(configs)}."
        )

    names: List[str] = sorted(configs.keys())
    matrix: DiffMatrix = {}

    for i, left in enumerate(names):
        for j, right in enumerate(names):
            if left == right:
                continue
            if not symmetric and j <= i:
                continue
            matrix[(left, right)] = diff_configs(configs[left], configs[right])

    return matrix


def matrix_summary(matrix: DiffMatrix) -> Dict[Tuple[str, str], str]:
    """Return a human-readable summary string for each pair in the matrix.

    Each summary line looks like::

        "3 added, 1 removed, 2 changed, 10 unchanged"

    Returns:
        Dict mapping the same (left, right) keys to summary strings.
    """
    from stackdiff.differ import summary as _summary

    return {pair: _summary(result) for pair, result in matrix.items()}


def most_divergent(matrix: DiffMatrix) -> Tuple[Tuple[str, str], int]:
    """Return the pair with the highest total number of differences.

    Differences are counted as added + removed + changed keys.

    Returns:
        A tuple of ``((left_name, right_name), diff_count)``.

    Raises:
        MatrixError: If the matrix is empty.
    """
    if not matrix:
        raise MatrixError("Cannot determine most divergent pair: matrix is empty.")

    def _diff_count(result: DiffResult) -> int:
        return (
            len(result.added)
            + len(result.removed)
            + len(result.changed)
        )

    best_pair = max(matrix, key=lambda p: _diff_count(matrix[p]))
    return best_pair, _diff_count(matrix[best_pair])


def as_table(matrix: DiffMatrix, names: List[str]) -> List[List[str]]:
    """Render the diff matrix as a 2-D list (suitable for tabular display).

    The first row and first column contain environment names.  Each cell
    contains the total diff count for that pair, or ``"-"`` on the diagonal.

    Args:
        matrix: The diff matrix produced by :func:`build_matrix`.
        names:  Ordered list of environment names to use as row/column headers.

    Returns:
        A list of rows; each row is a list of strings.
    """
    header = [""] + names
    rows: List[List[str]] = [header]

    for left in names:
        row: List[str] = [left]
        for right in names:
            if left == right:
                row.append("-")
            else:
                result = matrix.get((left, right)) or matrix.get((right, left))
                if result is None:
                    row.append("n/a")
                else:
                    total = len(result.added) + len(result.removed) + len(result.changed)
                    row.append(str(total))
        rows.append(row)

    return rows
