import csv
import os

def facPath(factionID):
	guildFolders = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{factionID}")]
	return f'./factions/{guildFolders[0]}'

def checkAndCreateDataFile(factionID):
	if 'factionData.csv' not in os.listdir(facPath(factionID)):
		print(f'[CONSOLE] Data file doesn\'t exist. Creating a new one')
		with open(f'{facPath(factionID)}/factionData.csv', 'w') as f:
			print('[CONSOLE] Created')
			pass

def checkAndWriteNewTemp(factionID,tempName, diffAt, diff):
	checkAndCreateDataFile(factionID)
	with open(f'{facPath(factionID)}/factionData.csv', 'r') as csv_file:
		csv_reader = csv.reader(csv_file)
		previous_lines = []
		for line in csv_reader:
			previous_lines.append(line)
		with open(f'{facPath(factionID)}/factionData.csv', 'w', newline='') as f:
			csv_writer = csv.writer(f, delimiter=',')
			temps = 0
			for line in previous_lines:
				if line[0] != tempName:
					csv_writer.writerow(line)
				else:
					temps = temps + 1
					print(f'Line 0: {line[0]}. Already exists')
					csv_writer.writerow(line)
			if temps == 1:
				print(f'[CONSOLE] Already exists as {tempName}.')
				f.close()
			else:	
				csv_writer.writerow([f'{tempName}', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'])
				print('[CONSOLE] Template did not exist. Created a new one')
				f.close()
		csv_file.close()

def writeNewNumeric(factionID,tempName, diffAt, diff):
	checkAndWriteNewTemp(factionID, tempName, diffAt, diff)
	print('[CONSOLE] Starting to write numeric data')
	with open(f'{facPath(factionID)}/factionData.csv', 'r') as csv_file:
		csv_reader = csv.reader(csv_file)
		previous_lines = []
		for line in csv_reader:
			previous_lines.append(line)
		with open(f'{facPath(factionID)}/factionData.csv', 'w', newline='') as f:
			csv_writer = csv.writer(f, delimiter=',')
			for line in previous_lines:
				if line[0] == tempName:
					print(f'Line: {line}')
					csv_writer.writerow([f'{tempName}', line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10], line[11], line[12], f'{diff}', f'{diffAt}'])
				else:
					print(f'Line: {line}')
					csv_writer.writerow(line)
			f.close()
		csv_file.close()

def readNumericData(factionID, tempName):
	print(f'[CONSOLE] Reading numeric data from template {tempName}')
	with open(f'{facPath(factionID)}/factionData.csv', 'r') as csv_file:
		csv_reader = csv.reader(csv_file)
		for line in csv_reader:
			if line[0] == tempName:
				processed_data = [float(line[1]), float(line[2]), float(line[3]), float(line[4]), float(line[5]), float(line[6]), float(line[7]), float(line[8]), float(line[9]), float(line[10]), float(line[11]), float(line[12])]
			else:
				pass
	return processed_data[0], processed_data[1], processed_data[2], processed_data[3], processed_data[4], processed_data[5], processed_data[6], processed_data[7], processed_data[8], processed_data[9], processed_data[10], processed_data[11] 


#tempName, diff1, diffAt1, diff2, diffAt2, diff3, diffAt3, diff4, diffAt4, diff5, diffAt5, diff6, diffAt6
#paraguai,0,0,0,0,0,0,0,0,0,0,12000,233333
#zambia,0,0,0,0,0,0,0,0,0,0,1200,2377733
#congo,0,0,0,0,0,0,0,0,0,0,1200,2377733
#brasil,0,0,0,0,0,0,0,0,0,0,1200,2377733