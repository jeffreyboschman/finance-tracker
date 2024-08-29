"""Utils for dealing with data from Notion API"""

from finance_tracker.connectors.notion_api import get_database


def get_page_name_mapping(database_id: str) -> dict:
    """
    Fetches all pages from the specified Notion database and creates a dictionary mapping
    page IDs to page names.

    Args:
        database_id (str): The ID of the Notion database containing the related pages.

    Returns:
        dict: A dictionary where the keys are page IDs and the values are the corresponding
            page names
    """
    # Fetch pages using the existing get_database function
    database_pages = get_database(database_id)

    page_name_mapping = {}
    for page in database_pages:
        page_id = page.get("id")
        page_name = (
            page.get("properties", {})
            .get("Name", {})
            .get("title", [{}])[0]
            .get("text", {})
            .get("content")
        )
        if page_id and page_name:
            page_name_mapping[page_id] = page_name

    return page_name_mapping


def extract_select_type_info(props: dict, column_name: str) -> str | None:
    """
    Extracts the selected option's name from a Notion database row JSON
    based on the specified column name.

    Args:
        props (dict): A dictionary representing properties of a Notion
            database row. It is expected to have a key corresponding to
            the specified column_name, which contains a dictionary with
            a "select" key representing the information for a Select type option.
        column_name (str): The name of a Select type column from which to extract
            the selected option name.

    Returns:
        str: The name of the selected option in the specified Select type column.
            If the selected option information is found, its name is
            returned. If the column does not exist or if the "select"
            key is null, None is returned.
    """
    select_dict = props.get(column_name, {}).get("select", None)
    if select_dict is not None:
        selected_option = select_dict.get("name", None)
    else:
        # Handle the case when "select" is null
        selected_option = None

    return selected_option


def extract_number_type_info(props: dict, column_name: str) -> str | None:
    """
    Extracts the number value from a Notion database row JSON
    based on the specified column name.

    Args:
        props (dict): A dictionary representing properties of a Notion
            database row. It is expected to have a key corresponding to
            the specified column_name, which contains a dictionary with
            a "number" key representing the information for a Number type column.

    Returns:
        str: The number value for the row. If the number information is not found, None is returned.
    """
    number_value = props.get(column_name, {}).get("number", None)
    return number_value


def extract_relation_type_info(props: dict, column_name: str) -> list | None:
    """
    Extracts the relation information from a Notion database row JSON
    based on the specified column name.

    Args:
        props (dict): A dictionary representing properties of a Notion
            database row. It is expected to have a key corresponding to
            the specified column_name, which contains a dictionary with
            a "relation" key representing the information for a Relation type column.
        column_name (str): The name of a Relation type column from which to extract
            the relation information.

    Returns:
        list: A list of linked page IDs for the relation. If the relation
            information is not found, None is returned.
    """
    relation_list = props.get(column_name, {}).get("relation", None)
    if relation_list is not None:
        # Extract page IDs from the relation (adjust based on your specific needs)
        # related_page_ids = [relation.get("name") for relation in relation_list]
        # return related_page_ids
        return relation_list
    return None
