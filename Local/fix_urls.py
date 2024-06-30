def add_prefix_to_lines(input_file, output_file, prefix):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    modified_lines = []
    for line in lines:
        if line.startswith('/'):
            modified_lines.append(f"{prefix}{line}")
        else:
            modified_lines.append(line)
    
    with open(output_file, 'w') as outfile:
        outfile.writelines(modified_lines)

if __name__ == "__main__":
    input_file = 'links.txt'   # Replace with your input file name
    output_file = 'modified_links.txt'  # Replace with your desired output file name
    prefix = 'https://www.onthesnow.com'  # Replace with the prefix string you want to add
    
    add_prefix_to_lines(input_file, output_file, prefix)
    print(f"Modified lines written to {output_file}")
