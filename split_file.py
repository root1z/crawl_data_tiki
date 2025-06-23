input_file = 'products.csv'
lines_per_file = 50000
num_files = 4

with open(input_file, 'r', encoding='utf-8') as infile:
    for part in range(1, num_files + 1):
        output_file = f'ids_part{part}.csv'
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for i in range(lines_per_file):
                line = infile.readline()
                if not line:
                    break
                outfile.write(line)
        if not line:
            break
print('Done splitting file.')