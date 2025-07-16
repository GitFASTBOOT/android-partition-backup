def parse_selection(selection, max_index):
    selection = selection.strip().lower()
    if selection in ('all', ''):
        return list(range(1, max_index + 1))

    indices = set()
    for part in selection.replace(' ', '').split(','):
        if '-' in part:
            start, end = part.split('-')
            try:
                start, end = int(start), int(end)
                indices.update(range(min(start, end), max(start, end) + 1))
            except ValueError:
                continue
        else:
            try:
                indices.add(int(part))
            except ValueError:
                continue
    return sorted(i for i in indices if 1 <= i <= max_index)
