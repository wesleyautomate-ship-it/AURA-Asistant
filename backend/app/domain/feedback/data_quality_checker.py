#!/usr/bin/env python3
"""
Data Quality Checker for Real Estate Data
Handles data validation, quality assessment, and error detection
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from collections import defaultdict

logger = logging.getLogger(__name__)


class DataQualityChecker:
    """Comprehensive data quality checker for real estate data"""

    def __init__(self):
        # Data validation patterns
        self.validation_patterns = {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "phone_uae": r"^(\+971|971|0)?[2-9]\d{8}$",
            "price_aed": r"^AED\s*[\d,]+(?:\.\d{2})?$",
            "date_formats": [
                r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
                r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
                r"\d{2}-\d{2}-\d{4}",  # DD-MM-YYYY
                r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}",
            ],
            "property_types": [
                "apartment",
                "villa",
                "penthouse",
                "townhouse",
                "studio",
                "duplex",
                "maisonette",
                "bungalow",
                "compound",
                "office",
                "retail",
                "warehouse",
            ],
            "dubai_areas": [
                "dubai marina",
                "downtown dubai",
                "palm jumeirah",
                "business bay",
                "jbr",
                "dubai hills",
                "emirates hills",
                "springs",
                "meadows",
                "lakes",
                "jumeirah",
                "al barsha",
                "al quoz",
                "al wasl",
                "al safa",
                "umm suqeim",
            ],
        }

        # Data quality thresholds
        self.quality_thresholds = {
            "completeness": 0.8,  # 80% of required fields should be filled
            "accuracy": 0.9,  # 90% of data should pass validation
            "consistency": 0.85,  # 85% of data should be consistent
            "uniqueness": 0.95,  # 95% of records should be unique
        }

    def check_data_quality(
        self, data: List[Dict], data_type: str = "transaction"
    ) -> Dict[str, Any]:
        """Comprehensive data quality assessment"""
        if not data:
            return {
                "status": "error",
                "message": "No data provided for quality check",
                "quality_score": 0,
            }

        # Convert to DataFrame for easier processing
        df = pd.DataFrame(data)

        # Run various quality checks
        completeness_score = self._check_completeness(df, data_type)
        accuracy_score = self._check_accuracy(df, data_type)
        consistency_score = self._check_consistency(df, data_type)
        uniqueness_score = self._check_uniqueness(df, data_type)

        # Calculate overall quality score
        overall_score = (
            completeness_score + accuracy_score + consistency_score + uniqueness_score
        ) / 4

        # Generate quality report
        quality_report = {
            "status": "success",
            "overall_quality_score": round(overall_score, 2),
            "quality_breakdown": {
                "completeness": round(completeness_score, 2),
                "accuracy": round(accuracy_score, 2),
                "consistency": round(consistency_score, 2),
                "uniqueness": round(uniqueness_score, 2),
            },
            "issues_found": self._identify_issues(df, data_type),
            "recommendations": self._generate_quality_recommendations(
                overall_score, data_type
            ),
            "data_summary": {
                "total_records": len(data),
                "total_fields": len(df.columns),
                "missing_values": df.isnull().sum().sum(),
                "duplicate_records": len(df) - len(df.drop_duplicates()),
            },
        }

        return quality_report

    def _check_completeness(self, df: pd.DataFrame, data_type: str) -> float:
        """Check data completeness"""
        if df.empty:
            return 0.0

        # Define required fields based on data type
        required_fields = self._get_required_fields(data_type)

        if not required_fields:
            return 1.0  # No required fields specified

        # Calculate completeness for required fields
        completeness_scores = []
        for field in required_fields:
            if field in df.columns:
                non_null_count = df[field].notna().sum()
                completeness_scores.append(non_null_count / len(df))
            else:
                completeness_scores.append(0.0)

        return (
            sum(completeness_scores) / len(completeness_scores)
            if completeness_scores
            else 0.0
        )

    def _check_accuracy(self, df: pd.DataFrame, data_type: str) -> float:
        """Check data accuracy"""
        if df.empty:
            return 0.0

        accuracy_scores = []

        # Check email accuracy
        if "email" in df.columns:
            email_accuracy = self._validate_emails(df["email"])
            accuracy_scores.append(email_accuracy)

        # Check phone accuracy
        if "phone" in df.columns:
            phone_accuracy = self._validate_phones(df["phone"])
            accuracy_scores.append(phone_accuracy)

        # Check price accuracy
        if "price" in df.columns or "transaction_value" in df.columns:
            price_field = "price" if "price" in df.columns else "transaction_value"
            price_accuracy = self._validate_prices(df[price_field])
            accuracy_scores.append(price_accuracy)

        # Check date accuracy
        date_fields = [col for col in df.columns if "date" in col.lower()]
        for date_field in date_fields:
            date_accuracy = self._validate_dates(df[date_field])
            accuracy_scores.append(date_accuracy)

        return sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 1.0

    def _check_consistency(self, df: pd.DataFrame, data_type: str) -> float:
        """Check data consistency"""
        if df.empty:
            return 0.0

        consistency_scores = []

        # Check property type consistency
        if "property_type" in df.columns:
            type_consistency = self._check_property_type_consistency(
                df["property_type"]
            )
            consistency_scores.append(type_consistency)

        # Check location consistency
        location_fields = [
            col
            for col in df.columns
            if "location" in col.lower() or "area" in col.lower()
        ]
        for location_field in location_fields:
            location_consistency = self._check_location_consistency(df[location_field])
            consistency_scores.append(location_consistency)

        # Check format consistency
        format_consistency = self._check_format_consistency(df)
        consistency_scores.append(format_consistency)

        return (
            sum(consistency_scores) / len(consistency_scores)
            if consistency_scores
            else 1.0
        )

    def _check_uniqueness(self, df: pd.DataFrame, data_type: str) -> float:
        """Check data uniqueness"""
        if df.empty:
            return 0.0

        # Check for exact duplicates
        total_records = len(df)
        unique_records = len(df.drop_duplicates())

        if total_records == 0:
            return 1.0

        return unique_records / total_records

    def _get_required_fields(self, data_type: str) -> List[str]:
        """Get required fields based on data type"""
        field_mappings = {
            "transaction": ["transaction_date", "transaction_value", "building_name"],
            "property": ["address", "price", "property_type"],
            "client": ["name", "email", "phone"],
            "agent": ["name", "license_number", "email"],
            "listing": ["property_type", "price", "location"],
        }

        return field_mappings.get(data_type, [])

    def _validate_emails(self, email_series: pd.Series) -> float:
        """Validate email addresses"""
        if email_series.empty:
            return 1.0

        valid_emails = 0
        total_emails = 0

        for email in email_series:
            if pd.notna(email) and str(email).strip():
                total_emails += 1
                if re.match(self.validation_patterns["email"], str(email)):
                    valid_emails += 1

        return valid_emails / total_emails if total_emails > 0 else 1.0

    def _validate_phones(self, phone_series: pd.Series) -> float:
        """Validate phone numbers"""
        if phone_series.empty:
            return 1.0

        valid_phones = 0
        total_phones = 0

        for phone in phone_series:
            if pd.notna(phone) and str(phone).strip():
                total_phones += 1
                phone_str = re.sub(r"[\s\-\(\)]", "", str(phone))
                if re.match(self.validation_patterns["phone_uae"], phone_str):
                    valid_phones += 1

        return valid_phones / total_phones if total_phones > 0 else 1.0

    def _validate_prices(self, price_series: pd.Series) -> float:
        """Validate price values"""
        if price_series.empty:
            return 1.0

        valid_prices = 0
        total_prices = 0

        for price in price_series:
            if pd.notna(price):
                total_prices += 1
                try:
                    # Try to convert to numeric
                    price_value = float(
                        str(price).replace(",", "").replace("AED", "").strip()
                    )
                    if price_value > 0:
                        valid_prices += 1
                except:
                    pass

        return valid_prices / total_prices if total_prices > 0 else 1.0

    def _validate_dates(self, date_series: pd.Series) -> float:
        """Validate date values"""
        if date_series.empty:
            return 1.0

        valid_dates = 0
        total_dates = 0

        for date in date_series:
            if pd.notna(date) and str(date).strip():
                total_dates += 1
                try:
                    pd.to_datetime(date)
                    valid_dates += 1
                except:
                    pass

        return valid_dates / total_dates if total_dates > 0 else 1.0

    def _check_property_type_consistency(self, type_series: pd.Series) -> float:
        """Check property type consistency"""
        if type_series.empty:
            return 1.0

        valid_types = 0
        total_types = 0

        for prop_type in type_series:
            if pd.notna(prop_type) and str(prop_type).strip():
                total_types += 1
                if str(prop_type).lower() in self.validation_patterns["property_types"]:
                    valid_types += 1

        return valid_types / total_types if total_types > 0 else 1.0

    def _check_location_consistency(self, location_series: pd.Series) -> float:
        """Check location consistency"""
        if location_series.empty:
            return 1.0

        valid_locations = 0
        total_locations = 0

        for location in location_series:
            if pd.notna(location) and str(location).strip():
                total_locations += 1
                if str(location).lower() in self.validation_patterns["dubai_areas"]:
                    valid_locations += 1

        return valid_locations / total_locations if total_locations > 0 else 1.0

    def _check_format_consistency(self, df: pd.DataFrame) -> float:
        """Check format consistency across the dataset"""
        if df.empty:
            return 1.0

        consistency_scores = []

        # Check for consistent data types
        for column in df.columns:
            if df[column].dtype == "object":
                # Check if all values in string column are strings
                string_count = sum(
                    isinstance(val, str) for val in df[column] if pd.notna(val)
                )
                total_count = df[column].notna().sum()
                if total_count > 0:
                    consistency_scores.append(string_count / total_count)

        return (
            sum(consistency_scores) / len(consistency_scores)
            if consistency_scores
            else 1.0
        )

    def _identify_issues(
        self, df: pd.DataFrame, data_type: str
    ) -> List[Dict[str, Any]]:
        """Identify specific data quality issues"""
        issues = []

        # Missing data issues
        missing_data = df.isnull().sum()
        for column, missing_count in missing_data.items():
            if missing_count > 0:
                issues.append(
                    {
                        "type": "missing_data",
                        "field": column,
                        "count": int(missing_count),
                        "percentage": round(missing_count / len(df) * 100, 2),
                        "severity": "high"
                        if missing_count / len(df) > 0.5
                        else "medium",
                    }
                )

        # Duplicate issues
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues.append(
                {
                    "type": "duplicates",
                    "count": int(duplicates),
                    "percentage": round(duplicates / len(df) * 100, 2),
                    "severity": "high" if duplicates / len(df) > 0.1 else "medium",
                }
            )

        # Format issues
        for column in df.columns:
            if df[column].dtype == "object":
                # Check for mixed data types
                type_counts = defaultdict(int)
                for val in df[column]:
                    if pd.notna(val):
                        type_counts[type(val).__name__] += 1

                if len(type_counts) > 1:
                    issues.append(
                        {
                            "type": "mixed_data_types",
                            "field": column,
                            "types_found": list(type_counts.keys()),
                            "severity": "medium",
                        }
                    )

        return issues

    def _generate_quality_recommendations(
        self, quality_score: float, data_type: str
    ) -> List[str]:
        """Generate recommendations based on quality score"""
        recommendations = []

        if quality_score < 0.5:
            recommendations.append(
                "Data quality is poor. Consider re-collecting or cleaning the data."
            )
        elif quality_score < 0.7:
            recommendations.append(
                "Data quality needs improvement. Review and clean the data before processing."
            )
        elif quality_score < 0.9:
            recommendations.append(
                "Data quality is good but could be improved with minor cleaning."
            )
        else:
            recommendations.append("Data quality is excellent. Ready for processing.")

        # Type-specific recommendations
        if data_type == "transaction":
            recommendations.append(
                "Ensure all transaction dates are in consistent format (YYYY-MM-DD)"
            )
            recommendations.append(
                "Verify that all prices are in AED and properly formatted"
            )
        elif data_type == "property":
            recommendations.append(
                "Standardize property types to use consistent naming"
            )
            recommendations.append("Verify all addresses are complete and accurate")
        elif data_type == "client":
            recommendations.append(
                "Ensure all email addresses are valid and properly formatted"
            )
            recommendations.append("Verify phone numbers are in UAE format (+971)")

        return recommendations

    def fix_common_issues(
        self, data: List[Dict], data_type: str
    ) -> Tuple[List[Dict], Dict[str, Any]]:
        """Fix common data quality issues"""
        if not data:
            return data, {"status": "error", "message": "No data provided"}

        df = pd.DataFrame(data)
        fixes_applied = []

        # Fix missing values
        for column in df.columns:
            if df[column].isnull().sum() > 0:
                if column in ["email", "phone"]:
                    # Remove rows with missing contact info
                    df = df.dropna(subset=[column])
                    fixes_applied.append(f"Removed rows with missing {column}")
                elif column in ["price", "transaction_value"]:
                    # Fill missing prices with median
                    median_price = df[column].median()
                    df[column] = df[column].fillna(median_price)
                    fixes_applied.append(f"Filled missing {column} with median value")
                else:
                    # Fill with appropriate default
                    if df[column].dtype == "object":
                        df[column] = df[column].fillna("Unknown")
                    else:
                        df[column] = df[column].fillna(0)
                    fixes_applied.append(f"Filled missing {column} with default value")

        # Remove duplicates
        original_count = len(df)
        df = df.drop_duplicates()
        if len(df) < original_count:
            fixes_applied.append(
                f"Removed {original_count - len(df)} duplicate records"
            )

        # Standardize formats
        for column in df.columns:
            if "date" in column.lower():
                df[column] = pd.to_datetime(df[column], errors="coerce")
                fixes_applied.append(f"Standardized date format for {column}")
            elif "price" in column.lower() or "value" in column.lower():
                df[column] = pd.to_numeric(df[column], errors="coerce")
                fixes_applied.append(f"Standardized numeric format for {column}")

        return df.to_dict("records"), {
            "status": "success",
            "fixes_applied": fixes_applied,
            "records_processed": len(data),
            "records_after_fixes": len(df),
        }
