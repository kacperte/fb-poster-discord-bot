import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os


# -------------------
# Google Sheets  Utils
# -------------------

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
FILE_URL = "https://docs.google.com/spreadsheets/d/1L4FPum32xhQEm0NPovsIVLad-qqO0ozNdRpTbdgPWXU"


def check_availability(day_of_the_week):
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_url(url=FILE_URL)
    worksheet = spreadsheet.get_worksheet(2)

    col_offset = (day_of_the_week - 1) * 5
    col_letter = chr(65 + col_offset)
    records_count = len(worksheet.col_values(ord(col_letter) - 64)) - 2

    other_days_info = []
    for i in range(1, 6):  # od poniedziałku do piątku
        other_col_offset = (i - 1) * 5
        other_col_letter = chr(65 + other_col_offset)
        other_records_count = len(worksheet.col_values(ord(other_col_letter) - 64)) - 2
        other_days_info.append(f"Dzień {i}: {6 - other_records_count}/6 wolnych slotów")

    if records_count >= 6:
        return False, f"Wszystkie sloty są zajęte dla dnia {day_of_the_week}. Prosze wybierz inny dzień lun usuń " \
                      f"zadanie.", other_days_info
    else:
        return True, f"Sloty dostępne dla dnia {day_of_the_week}: {6 - records_count}/6", other_days_info


def add_new_job_to_sheet(day_of_the_week, material_id, recruiter, groups_name, info):
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_url(url=FILE_URL)
    worksheet = spreadsheet.get_worksheet(2)

    col_offset = (day_of_the_week - 1) * 5

    col_letter = chr(65 + col_offset)
    first_empty_row = len(worksheet.col_values(ord(col_letter) - 64)) + 1

    is_available, message, other_days_info = check_availability(day_of_the_week=day_of_the_week)
    if is_available:
        worksheet.update_cell(first_empty_row, 1 + col_offset, info)
        worksheet.update_cell(first_empty_row, 2 + col_offset, recruiter)
        worksheet.update_cell(first_empty_row, 3 + col_offset, material_id)
        worksheet.update_cell(first_empty_row, 4 + col_offset, groups_name)
        return "Zadanie dodane do harmonogramu"
    else:
        return message, other_days_info

