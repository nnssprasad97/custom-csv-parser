"""Custom CSV Parser Implementation.

This module provides custom implementations of CSV reader and writer classes
that handle parsing and serialization of CSV data without relying on Python's
built-in csv module.
"""


class CustomCsvReader:
    """A streaming CSV reader that reads one row at a time.
    
    Implements the iterator protocol to efficiently parse CSV files
    without loading the entire file into memory.
    """
    
    def __init__(self, filepath):
        """Initialize the reader with a file path.
        
        Args:
            filepath: Path to the CSV file to read.
        """
        self.filepath = filepath
        self.file = None
        self.buffer = ''
        self.eof = False
    
    def __enter__(self):
        """Context manager entry."""
        self.file = open(self.filepath, 'r', encoding='utf-8')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.file:
            self.file.close()
    
    def __iter__(self):
        """Return self as an iterator."""
        if not self.file:
            self.file = open(self.filepath, 'r', encoding='utf-8')
        return self
    
    def __next__(self):
        """Parse and return the next row.
        
        Returns:
            A list of field values for the next row.
            
        Raises:
            StopIteration: When the end of file is reached.
        """
        if self.eof and not self.buffer:
            raise StopIteration
        
        row = self._read_row()
        if row is None:
            raise StopIteration
        
        return row
    
    def _read_row(self):
        """Read and parse a single row from the CSV file.
        
        Returns:
            A list of field values, or None if EOF is reached.
        """
        fields = []
        current_field = ''
        in_quotes = False
        
        while True:
            # Read more data if buffer is empty
            if not self.buffer and not self.eof:
                chunk = self.file.read(4096)
                if not chunk:
                    self.eof = True
                else:
                    self.buffer += chunk
            
            # Process buffer character by character
            if self.buffer:
                char = self.buffer[0]
                self.buffer = self.buffer[1:]
                
                if char == '"':
                    if in_quotes:
                        # Check for escaped quote
                        if self.buffer and self.buffer[0] == '"':
                            current_field += '"'
                            self.buffer = self.buffer[1:]
                        else:
                            in_quotes = False
                    else:
                        in_quotes = True
                
                elif char == ',' and not in_quotes:
                    fields.append(current_field)
                    current_field = ''
                
                elif char == '\n' and not in_quotes:
                    fields.append(current_field)
                    return fields if fields or current_field else None
                
                elif char == '\r':
                    # Handle Windows line endings
                    if self.buffer and self.buffer[0] == '\n':
                        self.buffer = self.buffer[1:]
                    if not in_quotes:
                        fields.append(current_field)
                        return fields if fields or current_field else None
                
                else:
                    current_field += char
            
            # EOF handling
            elif self.eof:
                if current_field or fields:
                    fields.append(current_field)
                    return fields
                return None


class CustomCsvWriter:
    """A CSV writer that writes rows to a CSV file.
    
    Properly handles quoting and escaping of fields containing
    special characters like commas, quotes, and newlines.
    """
    
    def __init__(self, filepath):
        """Initialize the writer with a file path.
        
        Args:
            filepath: Path where the CSV file should be written.
        """
        self.filepath = filepath
        self.file = None
    
    def __enter__(self):
        """Context manager entry."""
        self.file = open(self.filepath, 'w', encoding='utf-8', newline='')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.file:
            self.file.close()
    
    def writerows(self, rows):
        """Write multiple rows to the CSV file.
        
        Args:
            rows: An iterable of rows, where each row is a list of field values.
        """
        for row in rows:
            self.writerow(row)
    
    def writerow(self, row):
        """Write a single row to the CSV file.
        
        Args:
            row: A list of field values to write.
        """
        if not self.file:
            self.file = open(self.filepath, 'w', encoding='utf-8', newline='')
        
        formatted_fields = []
        for field in row:
            formatted_fields.append(self._format_field(str(field)))
        
        line = ','.join(formatted_fields) + '\n'
        self.file.write(line)
    
    def _format_field(self, field):
        """Format a field for CSV output with proper quoting and escaping.
        
        Args:
            field: The field value as a string.
            
        Returns:
            The properly formatted and quoted field.
        """
        # Check if field needs quoting
        if ',' in field or '"' in field or '\n' in field or '\r' in field:
            # Escape double quotes by doubling them
            escaped_field = field.replace('"', '""')
            return f'"{escaped_field}"'
        return field
