import csv

data_position = 11 # Pre-determined column of the csv file with data to process

# Set the name conventions
csv_file_path = '/Users/yevhenvoitiuk/Desktop/Capstone/Wireshark Captures/'
csv_name = 'csv_test.csv'

# Open the output file
with open(csv_file_path + "PROCESSED " + csv_name, mode="w") as output_csv:
    output_file = csv.writer(output_csv)

    # Open the input file
    with open(csv_file_path + 'csv_test.csv') as input_csv:
        input_file = csv.reader(input_csv)

        # Modify the first row to have the custom Attack column
        first_row = next(input_file)
        output_file.writerow(['Attack?'] + first_row)

        # Process other rows
        for row in input_file:
            tempRow = row
            if tempRow[data_position].startswith('3030', 2): # Goal is to change this substring to '3035' for machine training purposes
                changedData = tempRow[data_position][0:5] + '5' + tempRow[data_position][6:len(tempRow[data_position])]
                tempRow[data_position] = changedData
                output_file.writerow([1] + tempRow)
            else:
                output_file.writerow([0] + tempRow)

