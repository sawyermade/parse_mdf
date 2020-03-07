import os, sys, argparse, numpy as np, matplotlib
import matplotlib.pyplot as plt
import json, pandas as pd

def save_json(table_dict):
	# Converts to lists
	new_table_dict = {}
	for table_count, table_list_dict in table_dict.items():
		for var_val, table in table_list_dict.items():
			if table_count not in new_table_dict.keys():
				new_table_dict.update({table_count : []})
			new_table_dict[table_count].append(table.tolist())

	# Saves json
	with open('tables.json', 'w') as jf:
		json.dump(new_table_dict, jf, indent=4, sort_keys=True)

def plot_tables(table_dict):
	# Checks if output folger exists
	out_dir = 'output'
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	# Goes through all the tables
	fig = plt.figure()
	for table_count, table_list_dict in table_dict.items():
		# Goes through each table in table_count table_list
		print(f'Table Count Group: {table_count}\nNumber of Tables: {len(table_list_dict.keys())}')
		for i, (var_val, table) in enumerate(table_list_dict.items()):
			# Plots Vout vs Iout NQ
			df = pd.DataFrame(table, columns= ['Vout_NQ(real)', 'Iout_Q(real)', 'Iout_NQ(real)', 'Vin_Q(real)', 'Iin_Q(real)', 'Vin_NQ(real)', 'Iin_NQ(real)'])
			x_l, y_l = 'Vout_NQ(real)', 'Iout_NQ(real)'
			x_i, y_i = 0, 2
			print(f'var_val: {var_val}')
			plt.plot(table[:, x_i], table[:, y_i], label="Vg = " + str(var_val))
			plt.text(df['Vout_NQ(real)'].max(), df['Iout_NQ(real)'].max(), "Vg = " + str(var_val))
			fig.suptitle(f'{table_count}: {i+1}')
			plt.xlabel(x_l)
			plt.ylabel(y_l)
			plt.close(fig)

		# Formatting stdout
		print()
	plt.show()
	# fig.savefig(os.path.join(out_dir, 'all.png'))

def print_tables(table_dict):
	# Goes through table counts
	for table_count, table_list in table_dict.items():
		print(f'Table Count Number: {table_count}\nNumber of Tables for Table Count: {len(table_list)}')
		for table in table_list:
			for line in table:
				for val in line:
					print(val, end=' ')
				print()
			print()

def parse_mdf(mdf_path):
	with open(mdf_path) as mdf:
		# Goes through mdf line by line
		table_dict = {}
		for line in mdf:
			# Checks if new table
			if line.strip().startswith('VAR Vgs(real)'):
				# Gets var vg value
				var_val = float(line.split('=')[-1].strip())

				# Goes through table
				count = 0
				table_vals_list = []
				for line in mdf:
					# Checks if end of table
					if line.startswith('END'):
						break

					# Ignores trash lines and comments
					if line.startswith('BEGIN') or line.startswith('%'):
						continue

					# Splits line and converts vals to float
					line_split = line.split()
					line_vals = np.asarray([float(l) for l in line_split])
					table_vals_list.append(line_vals)
					count += 1
				
				# Adds table to table dict
				if str(count) not in table_dict.keys():
					table_dict.update({str(count) : {}})
				# table_dict[str(count)].append(np.asarray(table_vals_list))
				table_dict[str(count)].update({var_val : table_vals_list})

		# Converts all to np arrays
		for table_count, table_list_dict in table_dict.items():
			for var_val, table_list in table_list_dict.items():
				table_dict[table_count][var_val] = np.asarray(table_dict[table_count][var_val])

		# Table dict
		return table_dict


def convert_to_mdm(table_dict):
	# Creates mdm from table dict
	mdm_dict = {}
	for table_count, table_list_dict in table_dict.items():
		# mdm list
		mdm_list = []

		# Get vg infor to create header
		vg_list = table_list_dict.keys()
		vg_list = [float(f) for f in vg_list]
		vg_list.sort()

		# Calcs vg stuff
		vg_min, vg_max, vg_num = vg_list[0], vg_list[-1], len(vg_list)
		vg_step = round((vg_max - vg_min) / vg_num, 3)
		# print(f'vg: min, max, num, step = {vg_min}, {vg_max}, {vg_num}, {vg_step}')

		# Calcs vd stuff
		table_list = table_list_dict[vg_list[0]]
		table_col = [float(f) for f in table_list[:, 0]]
		vd_min, vd_max, vd_num = 0.05, round(max(table_col) / 10, 1) * 10, len(table_col)
		vd_step = round((vd_max - vd_min) / vd_num, 3)
		vd_list = [round(f*vd_step + vd_min, 3) for f in range(vd_num-1)]
		vd_list.append(vd_max)
		# print(vd_list)

		# Creates header
		header_list = [
			'! VERSION = 6.00',
			'BEGIN_HEADER',
			' ICCAP_INPUTS',
			f'  vd\tV D GROUND SMU1 0.03 LIN\t1\t{vd_min}\t{vd_max}\t{vd_num}\t{vd_step}',
			f'  vg\tV G GROUND SMU2 0.01 LIN\t1\t{vg_min}\t{vg_max}\t{vg_num}\t{vg_step}',
			f'  vs\tV S GROUND GND 0 CON\t0',
			f'  vb\tV B GROUND GND 0 CON\t0',
			' ICCAP_OUTPUTS',
			f'  id\tI D GROUND SMU1 B',
			f'  ig\tI G GROUND SMU1 B',
			' ICCAP_VALUES',
			'  W \"100u\"',
			'  L \"0.24u\"',
			'  RcontactDC \"1\"',
  			'  Rtotalport1 \"1\"',
			'  Rtotalport2\"1\"',
			'  TEMP \"27\"',
			'  TNOM \"27.00\"',
			'  TIMEDATE \"\"',
			'  OPERATOR \"\"',
			'  TECHNO \"myTechno\"',
			'  LOT \"myLot\"',
			'  WAFER \"myWafer\"',
			'  CHIP \"myChip\"',
			'  MODULE \"myModule\"',
			'  DEV_NAME \"myDevice\"',
			'  REMARKS \"my Notes\"',
			'END_HEADER',

		]
		# print(header_list)
		mdm_list += header_list

		# Create DBs
		for vg in vg_list:
			# Creates db list and goes though vals
			db_list = [float(f) for f in table_dict[table_count][vg][:, 2]]

			# Write DB header
			mdm_list.append('\nBEGIN_DB')
			mdm_list.append(f' ICCAP_VAR vg\t{vg}')
			mdm_list.append(f' ICCAP_VAR vs\t0')
			mdm_list.append(f' ICCAP_VAR vb\t0')
			mdm_list.append(f'\n#vd\t\tid\t\tig')

			# Writes all id vals from Iout NQ real
			for vd, id_val in zip(vd_list, db_list):
				mdm_list.append(f' {vd}\t\t{id_val:e}\t\t0')
			mdm_list.append('END_DB')

		# Adds to mdm lists
		mdm_dict.update({table_count : mdm_list})

	# Returns dict of mdms
	return mdm_dict

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input', help='input mdf file path', type=str)
	parser.add_argument('-o', '--output', help='output mdm file path', type=str)
	return parser.parse_args()

def write_mdm(mdm_dict):
	# Writes mdm files
	for table_count, mdm_list in mdm_dict.items():
		# Creates file name and writes file
		fname = f'{table_count}.mdm'
		with open(fname, 'w') as of:
			of.write('\n'.join(mdm_list))

def main():
	# Gets args
	args = parse_args()

	# Parses mdf file to np arrays
	table_dict = parse_mdf(args.input)
	# plot_tables(table_dict)
	# save_json(table_dict)
	mdm_dict = convert_to_mdm(table_dict)

	# Writes mdms
	write_mdm(mdm_dict)

if __name__ == '__main__':
	main()