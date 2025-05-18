from typing import List, Dict

def generate_size_options(
    original_width: int,
    original_height: int,
    tolerance: float = 0.05
) -> List[Dict[str, int]]:
    max_width = 1200
    max_height = 10000
    step = 100
    aspect_ratio = original_width / original_height
    results = []

    for target_height in range(step, max_height + 1, step):
        real_width = target_height * aspect_ratio
        rounded_width = round(real_width / step) * step

        if rounded_width < step or rounded_width > max_width:
            continue

        # ограничение на общее количество пикселей
        if (rounded_width * target_height) > 1000000:
            continue

        error = abs(real_width - rounded_width) / real_width

        if error <= tolerance:
            results.append({
                "width": rounded_width,
                "height": target_height,
                "error": error
            })

    if not results:
        return []

    min_error = min(r["error"] for r in results)
    best_fits = [r for r in results if r["error"] == min_error]

    for r in best_fits:
        del r["error"]

    return best_fits