import time

def generate_progress_bar(progress: float, started_at: float, eta: int, bar_width: int = 22) -> str:
    # Ограничим прогресс в пределах 0–100
    progress = max(0.0, min(progress, 100.0))

    # Прогресс от 0 до 100, слева направо
    filled_char = '▮'
    empty_char = '▯'
    full_blocks = int(progress / 100 * bar_width)
    empty_blocks = bar_width - full_blocks
    bar = filled_char * full_blocks + empty_char * empty_blocks

    percent_str = f"{progress:.4f}%"
    padding = (bar_width * 2 - len(percent_str)) // 2
    percent_line = ' ' * max(padding, 0) + percent_str

    elapsed = int(time.time() - started_at)
    minutes = elapsed // 60
    seconds = elapsed % 60
    timer_str = f"⏱ {minutes:02d}:{seconds:02d}"

    # ETA таймер
    eta_minutes = eta // 60
    eta_seconds = eta % 60
    eta_str = f"⌛ {eta_minutes:02d}:{eta_seconds:02d}"

    return f"🎴 Генерация эмодзи-пака\n\n{bar}\n\n{percent_line}\n\n{timer_str} | {eta_str}"
