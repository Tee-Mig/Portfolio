import sys


def ft_tqdm(lst: range) -> None:
    bar_width = 170
    total = len(lst)
    for i, item in enumerate(lst, 1):
        progress = (i / total) * 100

        bar_filled = int((i * bar_width) // total)
        bar = '█' * bar_filled + ' ' * (bar_width - bar_filled)
        sys.stdout.write(f'{int(progress)}%|{bar}| {i}/{total}\r')
        sys.stdout.flush()

        yield item
