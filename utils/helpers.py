async def convert_categories_to_string(categories) -> str:
    return ''.join([f'{categories[i]}\n' for i in range(0, len(categories))])

