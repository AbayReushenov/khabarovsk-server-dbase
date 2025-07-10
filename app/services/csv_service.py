"""CSV processing service for sales data.

This module handles CSV file validation, parsing, and transformation
for sales data import into the database.
"""

import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Tuple
import pandas as pd

from app.utils.logger import app_logger
from app.models.schemas import SalesDataRow


class CSVService:
    """Service for CSV file processing and validation."""

    def __init__(self):
        """Initialize CSV service."""
        self.required_columns = {
            'sku_id': ['sku_id', 'sku', 'product_id', 'id'],
            'date': ['date', 'sales_date', 'transaction_date'],
            'units_sold': ['units_sold', 'quantity', 'qty', 'units'],
            'revenue': ['revenue', 'sales', 'amount', 'total']
        }

        self.optional_columns = {
            'weather_temp': ['weather_temp', 'temperature', 'temp'],
            'season': ['season', 'period', 'season_name']
        }

        app_logger.info("CSVService initialized")

    def _detect_column_mapping(self, columns: List[str]) -> Dict[str, str]:
        """Detect column mapping from CSV headers.

        Args:
            columns: List of column names from CSV

        Returns:
            Dictionary mapping standard names to actual column names
        """
        mapping = {}
        columns_lower = [col.lower().strip() for col in columns]

        # Map required columns
        for standard_name, possible_names in self.required_columns.items():
            for possible_name in possible_names:
                if possible_name.lower() in columns_lower:
                    original_idx = columns_lower.index(possible_name.lower())
                    mapping[standard_name] = columns[original_idx]
                    break

        # Map optional columns
        for standard_name, possible_names in self.optional_columns.items():
            for possible_name in possible_names:
                if possible_name.lower() in columns_lower:
                    original_idx = columns_lower.index(possible_name.lower())
                    mapping[standard_name] = columns[original_idx]
                    break

        app_logger.info(f"Detected column mapping: {mapping}")
        return mapping

    def _validate_required_columns(self, mapping: Dict[str, str]) -> List[str]:
        """Validate that all required columns are present.

        Args:
            mapping: Column mapping dictionary

        Returns:
            List of missing required columns
        """
        missing_columns = []

        for required_col in self.required_columns.keys():
            if required_col not in mapping:
                missing_columns.append(required_col)

        return missing_columns

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string into datetime object.

        Args:
            date_str: Date string in various formats

        Returns:
            Parsed datetime object

        Raises:
            ValueError: If date cannot be parsed
        """
        date_formats = [
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%d.%m.%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S'
        ]

        for date_format in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), date_format)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse date: {date_str}")

    def _validate_and_transform_row(
        self,
        row: Dict[str, Any],
        mapping: Dict[str, str],
        row_number: int
    ) -> Tuple[SalesDataRow, List[str]]:
        """Validate and transform a single row of data.

        Args:
            row: Raw row data from CSV
            mapping: Column mapping dictionary
            row_number: Row number for error reporting

        Returns:
            Tuple of (transformed SalesDataRow, list of errors)
        """
        errors = []

        try:
            # Extract required fields
            sku_id = str(row[mapping['sku_id']]).strip()
            if not sku_id:
                errors.append(f"Row {row_number}: SKU ID is empty")

            # Parse date
            try:
                date = self._parse_date(row[mapping['date']])
            except ValueError as e:
                errors.append(f"Row {row_number}: {str(e)}")
                date = datetime.now()  # Fallback

            # Parse units sold
            try:
                units_sold = int(float(str(row[mapping['units_sold']]).replace(',', '')))
                if units_sold < 0:
                    errors.append(f"Row {row_number}: Units sold cannot be negative")
                    units_sold = 0
            except (ValueError, TypeError):
                errors.append(f"Row {row_number}: Invalid units sold value")
                units_sold = 0

            # Parse revenue
            try:
                revenue = float(str(row[mapping['revenue']]).replace(',', '').replace('$', ''))
                if revenue < 0:
                    errors.append(f"Row {row_number}: Revenue cannot be negative")
                    revenue = 0.0
            except (ValueError, TypeError):
                errors.append(f"Row {row_number}: Invalid revenue value")
                revenue = 0.0

            # Parse optional fields
            weather_temp = None
            if 'weather_temp' in mapping and mapping['weather_temp'] in row:
                try:
                    temp_value = row[mapping['weather_temp']]
                    if temp_value and str(temp_value).strip():
                        weather_temp = float(str(temp_value).replace(',', ''))
                except (ValueError, TypeError):
                    errors.append(f"Row {row_number}: Invalid temperature value")

            season = None
            if 'season' in mapping and mapping['season'] in row:
                season_value = row[mapping['season']]
                if season_value and str(season_value).strip():
                    season = str(season_value).strip()

            # Create SalesDataRow
            sales_row = SalesDataRow(
                sku_id=sku_id,
                date=date,
                units_sold=units_sold,
                revenue=revenue,
                weather_temp=weather_temp,
                season=season
            )

            return sales_row, errors

        except Exception as e:
            errors.append(f"Row {row_number}: Unexpected error: {str(e)}")
            # Return minimal valid row
            return SalesDataRow(
                sku_id="INVALID",
                date=datetime.now(),
                units_sold=0,
                revenue=0.0
            ), errors

    def validate_and_parse_csv(
        self,
        file_content: bytes,
        filename: str
    ) -> Tuple[List[Dict[str, Any]], List[str], int]:
        """Validate and parse CSV file content.

        Args:
            file_content: Raw CSV file content
            filename: Original filename for error reporting

        Returns:
            Tuple of (parsed data list, errors list, total rows processed)
        """
        app_logger.info(f"Processing CSV file: {filename}")

        try:
            # Decode file content
            content_str = file_content.decode('utf-8-sig')  # Handle BOM
        except UnicodeDecodeError:
            try:
                content_str = file_content.decode('latin1')
            except UnicodeDecodeError:
                return [], ["File encoding not supported. Please use UTF-8 or Latin1."], 0

        # Parse CSV
        try:
            csv_file = io.StringIO(content_str)

            # Try to detect delimiter
            sample = content_str[:1024]
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            csv_reader = csv.DictReader(csv_file, delimiter=delimiter)

            # Get column headers
            fieldnames = csv_reader.fieldnames
            if not fieldnames:
                return [], ["CSV file has no headers"], 0

            app_logger.info(f"CSV columns detected: {fieldnames}")

            # Detect column mapping
            mapping = self._detect_column_mapping(fieldnames)

            # Validate required columns
            missing_columns = self._validate_required_columns(mapping)
            if missing_columns:
                return [], [f"Missing required columns: {', '.join(missing_columns)}"], 0

            # Process rows
            parsed_data = []
            all_errors = []
            row_count = 0

            for i, row in enumerate(csv_reader, start=2):  # Start from 2 (header is row 1)
                row_count += 1

                # Skip empty rows
                if not any(str(value).strip() for value in row.values()):
                    continue

                sales_row, row_errors = self._validate_and_transform_row(row, mapping, i)
                all_errors.extend(row_errors)

                # Only add row if SKU ID is valid
                if sales_row.sku_id != "INVALID":
                    parsed_data.append(sales_row.dict())

            app_logger.info(f"CSV processing completed: {len(parsed_data)} valid rows, {len(all_errors)} errors")

            return parsed_data, all_errors, row_count

        except csv.Error as e:
            app_logger.error(f"CSV parsing error: {e}")
            return [], [f"CSV parsing error: {str(e)}"], 0

        except Exception as e:
            app_logger.error(f"Unexpected error processing CSV: {e}")
            return [], [f"Unexpected error: {str(e)}"], 0

    def generate_sample_csv(self) -> str:
        """Generate sample CSV content for download.

        Returns:
            Sample CSV content as string
        """
        sample_data = [
            ['sku_id', 'date', 'units_sold', 'revenue', 'weather_temp', 'season'],
            ['DOWN_JACKET_001', '2024-01-15', '5', '15000.00', '-15.5', 'winter'],
            ['DOWN_JACKET_002', '2024-01-16', '3', '9500.00', '-12.0', 'winter'],
            ['DOWN_JACKET_001', '2024-01-17', '7', '21000.00', '-18.2', 'winter'],
            ['DOWN_JACKET_003', '2024-01-18', '2', '8000.00', '-10.5', 'winter'],
        ]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(sample_data)

        return output.getvalue()


# Global instance
csv_service = CSVService()
