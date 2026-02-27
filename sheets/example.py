from .service import get_service
from googleapiclient.errors import HttpError


def get_names_and_majors():
    """
    Shows basic usage of the Sheets API.
    Gets values from a sample spreadsheet.
    You can view the spreadsheet at https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    SAMPLE_RANGE_NAME = "Class Data!A2:E"

    try:
        # Call the Sheets API
        sheet = get_service().spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            return []

        # columns A and E (0-indexed)
        return [f"{row[0]}, {row[4]}" for row in values]
    except HttpError as err:
        print(err)
        return []