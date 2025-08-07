from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"


def get_heuristics():
    """
    Load heuristics from a predefined file.

    Returns:
        dict: A dictionary where keys are heuristic names and values are the corresponding heuristic file paths.
    """
    heuristics_directory = STATIC_DIR / "heuristics"
    result = {}
    for fname in heuristics_directory.glob("*_heuristic.py"):
        heuristic_name = fname.name.replace("_heuristic.py", "")
        result[heuristic_name] = fname
    return result
