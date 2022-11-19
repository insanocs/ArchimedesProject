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
				csv_writer.writerow([f'{tempName}', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0'])
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
					row = []
					row.append(f'{tempName}')
					for i in range(3,33):
						row.append(line[i])
					row.append(f'{diff}')
					row.append(f'{diffAt}')
					csv_writer.writerow(row)
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
				processed_data = []
				for i in range(1,len(line)):
					processed_data.append(float(line[i]))
			else:
				pass
	print('[CONSOLE] Returning data to function')
	return processed_data
