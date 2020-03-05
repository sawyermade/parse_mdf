import os, sys, argparse, numpy as np, matplotlib
import matplotlib.pyplot as plt
import json

def save_json(table_dict):
	# Converts to lists
	new_table_dict = {}
	for table_count, table_list in table_dict.items():
		new_table_dict.update({table_count : table_list.tolist()})

	# Saves json
	with open('tables.json', 'w') as jf:
		json.dump(new_table_dict, jf, indent=4, sort_keys=True)

def plot_tables(table_dict):
	# Checks if output folger exists
	out_dir = 'output'
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	# Goes through all the tables
	for table_count, table_list in table_dict.items():
		# Goes through each table in table_count table_list
		print(f'Table Count Group: {table_count}\nNumber of Tables: {len(table_list)}')
		for i, table in enumerate(table_list):
			# Plots Vout vs Iout NQ
			x_l, y_l = 'Vout_NQ(real)', 'Iout_NQ(real)'
			x_i, y_i = 0, 2
			fig = plt.figure()
			plt.plot(table[:, x_i], table[:, y_i])
			fig.suptitle(f'{table_count}: {i+1}')
			plt.xlabel(x_l)
			plt.ylabel(y_l)
			# plt.show()
			fig.savefig(os.path.join(out_dir, f'{table_count}_{i+1}'))
			plt.close(fig)

		# Formatting stdout
		print()

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
					table_dict.update({str(count) : []})
				table_dict[str(count)].append(np.asarray(table_vals_list))

		# Converts all to np arrays
		for table_count, table_list in table_dict.items():
			table_dict[table_count] = np.asarray(table_dict[table_count])

		# Table dict
		return table_dict

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input', help='input mdf file path', type=str)
	parser.add_argument('-o', '--output', help='output mdm file path', type=str)
	return parser.parse_args()

def main():
	# Gets args
	args = parse_args()

	# Parses mdf file to np arrays
	table_dict = parse_mdf(args.input)
	plot_tables(table_dict)
	save_json(table_dict)

if __name__ == '__main__':
	main()