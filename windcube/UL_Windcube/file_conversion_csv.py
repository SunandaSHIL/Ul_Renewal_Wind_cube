from glob import glob
import os
import csv
import shutil
# import pandas as pd
from UL_Windcube.utility import create_directories


class ConvertingFile:
    def __init__(self, year, month) -> None:
        self.year = year
        self.month = month
        self.total_count = 0
        self.current_dir = os.getcwd()
        self.start_keyword = 'Timestamp (end of interval)'

        self.new_csv_path, self.new_csv_year_path, self.new_csv_month_path = (
            create_directories("New", self.year, self.month, self.current_dir)
        )
        (
            self.processed_csv_path, self.processed_csv_year_path, self.processed_csv_month_path,
        ) = create_directories("Converted_csv_files", self.year, self.month, self.current_dir)

    def read_sta_file(self, source_file_path):
        """
        Reads the content of a .sta file starting from the row containing the start_keyword.
        """
        data = []

        with open(source_file_path, 'r', encoding='latin1', errors='ignore') as file:
            lines = file.readlines()

            start_reading = False
            for line in lines:
                if start_reading:
                    row = line.strip().split('\t')
                    data.append(row)
                elif self.start_keyword in line:
                    start_reading = True
                    # Include the row containing the keyword
                    row = line.strip().split('\t')
                    data.append(row)
        return data

    def remove_empty_columns(self, data):
        """
        Removes columns that are completely empty from the data.
        """
        # Transpose the data to work with columns
        transposed_data = list(map(list, zip(*data)))

        # Filter out columns that are entirely empty
        filtered_columns = [col for col in transposed_data if any(cell.strip() for cell in col)]

        # Transpose back to row-wise data
        cleaned_data = list(map(list, zip(*filtered_columns)))
        return cleaned_data

    def write_csv_file(self, data, output_file_path):
        """
        Writes data to a .csv file.
        """
        with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in data:
                writer.writerow(row)

    def convert_sta_to_csv(self):
        """
        Converts a .sta file to a .csv file starting from the row containing the start_keyword.
        """
        for csv_file in os.listdir(self.new_csv_month_path):
            if csv_file.endswith(".sta"):
                source_file_path = os.path.join(self.new_csv_month_path, csv_file)

                # Generate a unique output file path
                base_name = os.path.basename(csv_file)
                file_name, _ = os.path.splitext(base_name)
                output_file_path = os.path.join(self.new_csv_month_path, f"{file_name}.csv")

                # Read and process the .sta file
                data = self.read_sta_file(source_file_path)
                cleaned_data = self.remove_empty_columns(data)

                # Write data to CSV file
                self.write_csv_file(cleaned_data, output_file_path)
                # Move the output file to the processed directory
                shutil.move(output_file_path, os.path.join(self.processed_csv_month_path, f"{file_name}.csv"))

