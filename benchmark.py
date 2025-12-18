"""Benchmark script for comparing custom CSV parser with Python's standard csv module."""

import csv
import random
import string
import timeit
import os
from csv_parser import CustomCsvReader, CustomCsvWriter


def generate_test_csv(filename, num_rows=10000, num_cols=5):
    """Generate a test CSV file with standard and edge cases.
    
    Args:
        filename: Path to the output CSV file.
        num_rows: Number of rows to generate.
        num_cols: Number of columns to generate.
    """
    with CustomCsvWriter(filename) as writer:
        # Write header
        header = [f'Column_{i}' for i in range(num_cols)]
        writer.writerow(header)
        
        # Write data rows with various edge cases
        for row_num in range(num_rows):
            row = []
            for col_num in range(num_cols):
                rand = random.random()
                if rand < 0.1:  # 10% quotes
                    value = f'Value with \"quotes\" {row_num},{col_num}'
                elif rand < 0.2:  # 10% commas
                    value = f'Value,with,commas,{row_num}'
                elif rand < 0.25:  # 5% newlines
                    value = f'Value\nwith\nnewlines {row_num}'
                else:  # 75% normal values
                    value = f'Value_{row_num}_{col_num}'
                row.append(value)
            writer.writerow(row)


def benchmark_read(csv_file, use_custom=True):
    """Benchmark reading a CSV file.
    
    Args:
        csv_file: Path to the CSV file.
        use_custom: If True, benchmark custom reader; if False, benchmark standard reader.
        
    Returns:
        Time in seconds.
    """
    if use_custom:
        def read_custom():
            with CustomCsvReader(csv_file) as reader:
                for _ in reader:
                    pass
        return timeit.timeit(read_custom, number=3) / 3
    else:
        def read_standard():
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                for _ in reader:
                    pass
        return timeit.timeit(read_standard, number=3) / 3


def benchmark_write(test_data, output_file, use_custom=True):
    """Benchmark writing a CSV file.
    
    Args:
        test_data: List of rows to write.
        output_file: Path to the output CSV file.
        use_custom: If True, benchmark custom writer; if False, benchmark standard writer.
        
    Returns:
        Time in seconds.
    """
    if use_custom:
        def write_custom():
            with CustomCsvWriter(output_file) as writer:
                writer.writerows(test_data)
        return timeit.timeit(write_custom, number=3) / 3
    else:
        def write_standard():
            with open(output_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerows(test_data)
        return timeit.timeit(write_standard, number=3) / 3


def run_benchmarks():
    """Run all benchmarks and print results."""
    test_csv = 'benchmark_test.csv'
    output_csv_custom = 'output_custom.csv'
    output_csv_standard = 'output_standard.csv'
    
    print('Generating test CSV file with 10,000 rows and 5 columns...')
    generate_test_csv(test_csv, num_rows=10000, num_cols=5)
    
    print('Running benchmarks...')
    print()
    
    # Benchmark reading
    print('=== READ BENCHMARK ===')
    custom_read_time = benchmark_read(test_csv, use_custom=True)
    standard_read_time = benchmark_read(test_csv, use_custom=False)
    
    print(f'Custom Reader: {custom_read_time:.4f} seconds')
    print(f'Standard Reader: {standard_read_time:.4f} seconds')
    print(f'Ratio (Custom/Standard): {custom_read_time/standard_read_time:.2f}x')
    print()
    
    # Benchmark writing
    print('=== WRITE BENCHMARK ===')
    # Generate test data
    test_data = []
    for i in range(5000):
        row = [f'Field_{i}_{j}' for j in range(5)]
        test_data.append(row)
    
    custom_write_time = benchmark_write(test_data, output_csv_custom, use_custom=True)
    standard_write_time = benchmark_write(test_data, output_csv_standard, use_custom=False)
    
    print(f'Custom Writer: {custom_write_time:.4f} seconds')
    print(f'Standard Writer: {standard_write_time:.4f} seconds')
    print(f'Ratio (Custom/Standard): {custom_write_time/standard_write_time:.2f}x')
    print()
    
    # Cleanup
    os.remove(test_csv)
    os.remove(output_csv_custom)
    os.remove(output_csv_standard)
    
    print('Benchmark complete!')


if __name__ == '__main__':
    run_benchmarks()
