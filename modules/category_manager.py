from storage import load_categories, save_categories


def add_post(category, file_id, text):

    data = load_categories()

    data[category]["posts"].append({
        "file_id": file_id,
        "text": text
    })

    save_categories(data)
