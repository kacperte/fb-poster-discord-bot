import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -------------------
# Google Sheets  Utils
# -------------------


def add_new_job_to_sheet(day_of_the_week, material_id, recruiter, groups, info):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    FILE_URL = "https://docs.google.com/spreadsheets/d/1L4FPum32xhQEm0NPovsIVLad-qqO0ozNdRpTbdgPWXU"
    credentials = ServiceAccountCredentials.from_json_keyfile_name("../iam-storage.json", scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_url(url=FILE_URL)
    worksheet = spreadsheet.get_worksheet(2)

    col_offset = (day_of_the_week - 1) * 4

    col_letter = chr(65 + col_offset)
    first_empty_row = len(worksheet.col_values(ord(col_letter) - 64)) + 1 1

    worksheet.update_cell(first_empty_row, 1 + col_offset, material_id)
    worksheet.update_cell(first_empty_row, 2 + col_offset, recruiter)
    worksheet.update_cell(first_empty_row, 3 + col_offset, groups)
    worksheet.update_cell(first_empty_row, 4 + col_offset, info)


add_new_job_to_sheet(day_of_the_week=2, material_id="M1", recruiter="R1", groups="G1", info="I1")
