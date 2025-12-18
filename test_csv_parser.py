"""Comprehensive test suite for CustomCsvReader and CustomCsvWriter.

This module provides exhaustive testing for all functionality, edge cases,
and requirements specified in the CSV Parser task.
"""

import csv
import os
import tempfile
from csv_parser import CustomCsvReader, CustomCsvWriter


class TestCsvParser:
    """Test class for CSV parser functionality."""

    def __init__(self):
        """Initialize test results tracking."""
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_details = []

    def assert_equal(self, actual, expected, test_name):
        """Assert equality and track results."""
        if actual == expected:
            self.tests_passed += 1
            self.test_details.append(f"✓ PASS: {test_name}")
        else:
            self.tests_failed += 1
            self.test_details.append(
                f"✗ FAIL: {test_name}\n  Expected: {expected}\n  Got: {actual}"
            )

    def test_reader_basic_parsing(self):
        """Test basic CSV parsing without special characters."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("name,age,city\n")
            f.write("Alice,28,New York\n")
            f.write("Bob,35,London\n")
            temp_file = f.name

        try:
            with CustomCsvReader(temp_file) as reader:
                rows = list(reader)
            
            self.assert_equal(len(rows), 3, "Basic parsing - row count")
            self.assert_equal(rows[0], ['name', 'age', 'city'], 
                            "Basic parsing - header row")
            self.assert_equal(rows[1], ['Alice', '28', 'New York'],
                            "Basic parsing - first data row")
            self.assert_equal(rows[2], ['Bob', '35', 'London'],
                            "Basic parsing - second data row")
        finally:
            os.unlink(temp_file)

    def test_reader_quoted_fields(self):
        """Test parsing with quoted fields."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write('name,description\n')
            f.write('"Alice","Works in New York"\n')
            f.write('"Bob","Likes, coffee"\n')
            temp_file = f.name

        try:
            with CustomCsvReader(temp_file) as reader:
                rows = list(reader)
            
            self.assert_equal(rows[1][1], 'Works in New York',
                            "Quoted fields - simple quote")
            self.assert_equal(rows[2][1], 'Likes, coffee',
                            "Quoted fields - comma inside quotes")
        finally:
            os.unlink(temp_file)

    def test_reader_escaped_quotes(self):
        """Test parsing with escaped quotes (" "" ")."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write('name,comment\n')
            f.write('"Alice","She said ""Hello"""\n')
            temp_file = f.name

        try:
            with CustomCsvReader(temp_file) as reader:
                rows = list(reader)
            
            self.assert_equal(rows[1][1], 'She said "Hello"',
                            "Escaped quotes - double quote escape")
        finally:
            os.unlink(temp_file)

    def test_reader_newlines_in_fields(self):
        """Test parsing with embedded newlines in quoted fields."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write('id,description\n')
            f.write('1,"Line 1\nLine 2\nLine 3"\n')
            f.write('2,Normal\n')
            temp_file = f.name

        try:
            with CustomCsvReader(temp_file) as reader:
                rows = list(reader)
            
            self.assert_equal('Line 1\nLine 2\nLine 3' in rows[1][1],
                            True, "Newlines in fields - multiline content")
            self.assert_equal(rows[2][1], 'Normal',
                            "Newlines in fields - normal field after")
        finally:
            os.unlink(temp_file)

    def test_writer_basic_writing(self):
        """Test basic CSV writing."""
        data = [
            ['name', 'age', 'city'],
            ['Alice', '28', 'New York'],
            ['Bob', '35', 'London']
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name

        try:
            with CustomCsvWriter(temp_file) as writer:
                writer.writerows(data)
            
            # Verify with standard csv reader
            with open(temp_file, 'r') as f:
                reader = csv.reader(f)
                written_rows = list(reader)
            
            self.assert_equal(written_rows, data,
                            "Basic writing - matches expected data")
        finally:
            os.unlink(temp_file)

    def test_writer_fields_with_commas(self):
        """Test writing fields containing commas."""
        data = [
            ['name', 'address'],
            ['Alice', '123 Main St, New York, NY']
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name

        try:
            with CustomCsvWriter(temp_file) as writer:
                writer.writerows(data)
            
            # Verify with standard csv reader
            with open(temp_file, 'r') as f:
                reader = csv.reader(f)
                written_rows = list(reader)
            
            self.assert_equal(written_rows[1][1],
                            '123 Main St, New York, NY',
                            "Fields with commas - properly quoted")
        finally:
            os.unlink(temp_file)

    def test_writer_fields_with_quotes(self):
        """Test writing fields containing quotes."""
        data = [
            ['name', 'quote'],
            ['Alice', 'She said "Hello"']
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name

        try:
            with CustomCsvWriter(temp_file) as writer:
                writer.writerows(data)
            
            # Verify with standard csv reader
            with open(temp_file, 'r') as f:
                reader = csv.reader(f)
                written_rows = list(reader)
            
            self.assert_equal(written_rows[1][1],
                            'She said "Hello"',
                            "Fields with quotes - properly escaped")
        finally:
            os.unlink(temp_file)

    def test_roundtrip_complex_data(self):
        """Test write then read with complex data."""
        original_data = [
            ['id', 'name', 'description'],
            ['1', 'Product A', 'Price: $19.99, 50% off'],
            ['2', 'Product B', 'Says "Best choice"\nin the market']
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name

        try:
            # Write with custom writer
            with CustomCsvWriter(temp_file) as writer:
                writer.writerows(original_data)
            
            # Read back with custom reader
            with CustomCsvReader(temp_file) as reader:
                read_data = list(reader)
            
            # Compare
            self.assert_equal(len(read_data), len(original_data),
                            "Roundtrip - row count matches")
            for i, row in enumerate(original_data):
                self.assert_equal(read_data[i], row,
                                f"Roundtrip - row {i} matches")
        finally:
            os.unlink(temp_file)

    def test_streaming_large_file(self):
        """Test streaming capability with large file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write('id,value\n')
            for i in range(1000):
                f.write(f'{i},data_{i}\n')
            temp_file = f.name

        try:
            row_count = 0
            with CustomCsvReader(temp_file) as reader:
                for row in reader:
                    row_count += 1
                    # Verify format
                    if row_count > 1:  # Skip header
                        assert len(row) == 2
            
            self.assert_equal(row_count, 1001,
                            "Streaming - large file (1000 rows + header)")
        finally:
            os.unlink(temp_file)

    def test_empty_fields(self):
        """Test handling of empty fields."""
        data = [
            ['a', 'b', 'c'],
            ['1', '', '3'],
            ['', '2', '']
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name

        try:
            with CustomCsvWriter(temp_file) as writer:
                writer.writerows(data)
            
            with CustomCsvReader(temp_file) as reader:
                read_data = list(reader)
            
            self.assert_equal(read_data, data,
                            "Empty fields - properly preserved")
        finally:
            os.unlink(temp_file)

    def test_windows_line_endings(self):
        """Test handling of Windows line endings (\r\n)."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as f:
            f.write(b'name,age\r\n')
            f.write(b'Alice,28\r\n')
            f.write(b'Bob,35\r\n')
            temp_file = f.name

        try:
            with CustomCsvReader(temp_file) as reader:
                rows = list(reader)
            
            self.assert_equal(len(rows), 3,
                            "Windows line endings - row count")
            self.assert_equal(rows[1][0], 'Alice',
                            "Windows line endings - data integrity")
        finally:
            os.unlink(temp_file)

    def run_all_tests(self):
        """Execute all tests."""
        print("\n" + "="*60)
        print("COMPREHENSIVE CSV PARSER TEST SUITE")
        print("="*60 + "\n")

        # Run all test methods
        self.test_reader_basic_parsing()
        self.test_reader_quoted_fields()
        self.test_reader_escaped_quotes()
        self.test_reader_newlines_in_fields()
        self.test_writer_basic_writing()
        self.test_writer_fields_with_commas()
        self.test_writer_fields_with_quotes()
        self.test_roundtrip_complex_data()
        self.test_streaming_large_file()
        self.test_empty_fields()
        self.test_windows_line_endings()

        # Print results
        print("\nTest Results:\n")
        for detail in self.test_details:
            print(detail)

        total = self.tests_passed + self.tests_failed
        print(f"\n{'-'*60}")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/total*100):.1f}%")
        print("="*60 + "\n")

        return self.tests_failed == 0


if __name__ == '__main__':
    tester = TestCsvParser()
    success = tester.run_all_tests()
    exit(0 if success else 1)
