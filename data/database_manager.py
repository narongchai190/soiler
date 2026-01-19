"""
S.O.I.L.E.R. Database Manager - Version 2.0
SQLite persistence layer for analysis history and data management.
Supports the new 9-agent architecture with Thai outputs.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class DatabaseManager:
    """
    Database Manager for S.O.I.L.E.R. system.

    Handles:
    - Analysis history storage
    - User session tracking
    - Data export/import
    """

    def __init__(self, db_path: str = None):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file. Defaults to data/soiler_v1.db
        """
        if db_path is None:
            # Get the directory where this file is located
            data_dir = Path(__file__).parent
            db_path = data_dir / "soiler_v1.db"

        self.db_path = str(db_path)
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """Initialize database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create analysis_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                location_name TEXT NOT NULL,
                lat REAL,
                lon REAL,
                crop_type TEXT NOT NULL,
                field_size_rai REAL,
                budget_thb REAL,
                soil_data TEXT,
                analysis_params TEXT,
                final_report TEXT,
                executive_summary TEXT,
                overall_score REAL,
                roi_percent REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create user_sessions table for future use
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                started_at TEXT NOT NULL,
                last_activity TEXT,
                total_analyses INTEGER DEFAULT 0
            )
        """)

        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON analysis_history(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_location ON analysis_history(location_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crop ON analysis_history(crop_type)
        """)

        conn.commit()
        conn.close()

    def save_analysis(
        self,
        location_name: str,
        crop_type: str,
        soil_data: Dict[str, Any],
        final_report: Dict[str, Any],
        lat: float = None,
        lon: float = None,
        field_size_rai: float = None,
        budget_thb: float = None,
        session_id: str = None,
        analysis_params: Dict[str, Any] = None
    ) -> int:
        """
        Save analysis result to database.

        Args:
            location_name: Name of the location
            crop_type: Type of crop analyzed
            soil_data: Dictionary containing soil parameters (pH, N, P, K, etc.)
            final_report: Complete analysis report from orchestrator
            lat: Latitude coordinate
            lon: Longitude coordinate
            field_size_rai: Field size in rai
            budget_thb: Budget in THB
            session_id: Optional session identifier
            analysis_params: Additional analysis parameters

        Returns:
            ID of the inserted record
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()

        # Extract summary data for quick access (v2.0 with Thai support)
        executive_summary = final_report.get("executive_summary", {})
        overall_score = executive_summary.get("overall_score", 0)

        # Support both old and new format for ROI
        dashboard = final_report.get("dashboard", {})
        roi_percent = dashboard.get("returns", {}).get("roi_percent", 0)

        # Extract Thai summary if available (v2.0)
        overall_status_th = executive_summary.get("overall_status_th", "")
        bottom_line_th = executive_summary.get("bottom_line_th", "")

        cursor.execute("""
            INSERT INTO analysis_history (
                timestamp, session_id, location_name, lat, lon,
                crop_type, field_size_rai, budget_thb,
                soil_data, analysis_params, final_report,
                executive_summary, overall_score, roi_percent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            session_id,
            location_name,
            lat,
            lon,
            crop_type,
            field_size_rai,
            budget_thb,
            json.dumps(soil_data, ensure_ascii=False),
            json.dumps(analysis_params, ensure_ascii=False) if analysis_params else None,
            json.dumps(final_report, ensure_ascii=False),
            json.dumps(executive_summary, ensure_ascii=False),
            overall_score,
            roi_percent
        ))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return record_id

    def get_recent_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent analysis history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of analysis records (summarized)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id, timestamp, location_name, lat, lon,
                crop_type, field_size_rai, budget_thb,
                overall_score, roi_percent, executive_summary
            FROM analysis_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            record = dict(row)
            # Parse executive_summary JSON
            if record.get("executive_summary"):
                try:
                    record["executive_summary"] = json.loads(record["executive_summary"])
                except json.JSONDecodeError:
                    record["executive_summary"] = {}
            results.append(record)

        return results

    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """
        Get full analysis record by ID.

        Args:
            analysis_id: ID of the analysis record

        Returns:
            Full analysis record with all data
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM analysis_history WHERE id = ?
        """, (analysis_id,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        record = dict(row)

        # Parse JSON fields
        for json_field in ["soil_data", "analysis_params", "final_report", "executive_summary"]:
            if record.get(json_field):
                try:
                    record[json_field] = json.loads(record[json_field])
                except json.JSONDecodeError:
                    record[json_field] = {}

        return record

    def get_history_by_location(self, location_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get analysis history for a specific location.

        Args:
            location_name: Name of the location
            limit: Maximum number of records to return

        Returns:
            List of analysis records for the location
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id, timestamp, location_name, crop_type,
                field_size_rai, overall_score, roi_percent
            FROM analysis_history
            WHERE location_name LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{location_name}%", limit))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_history_by_crop(self, crop_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get analysis history for a specific crop type.

        Args:
            crop_type: Type of crop
            limit: Maximum number of records to return

        Returns:
            List of analysis records for the crop
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id, timestamp, location_name, crop_type,
                field_size_rai, overall_score, roi_percent
            FROM analysis_history
            WHERE crop_type LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{crop_type}%", limit))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics from the database.

        Returns:
            Dictionary with various statistics
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        # Total analyses
        cursor.execute("SELECT COUNT(*) as count FROM analysis_history")
        stats["total_analyses"] = cursor.fetchone()["count"]

        # Average score
        cursor.execute("SELECT AVG(overall_score) as avg FROM analysis_history")
        result = cursor.fetchone()["avg"]
        stats["average_score"] = round(result, 1) if result else 0

        # Average ROI
        cursor.execute("SELECT AVG(roi_percent) as avg FROM analysis_history")
        result = cursor.fetchone()["avg"]
        stats["average_roi"] = round(result, 1) if result else 0

        # Analyses by crop
        cursor.execute("""
            SELECT crop_type, COUNT(*) as count
            FROM analysis_history
            GROUP BY crop_type
        """)
        stats["by_crop"] = {row["crop_type"]: row["count"] for row in cursor.fetchall()}

        # Analyses by location
        cursor.execute("""
            SELECT location_name, COUNT(*) as count
            FROM analysis_history
            GROUP BY location_name
        """)
        stats["by_location"] = {row["location_name"]: row["count"] for row in cursor.fetchall()}

        # Recent activity (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM analysis_history
            WHERE timestamp >= datetime('now', '-7 days')
        """)
        stats["last_7_days"] = cursor.fetchone()["count"]

        conn.close()
        return stats

    def delete_analysis(self, analysis_id: int) -> bool:
        """
        Delete an analysis record.

        Args:
            analysis_id: ID of the analysis to delete

        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM analysis_history WHERE id = ?", (analysis_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted

    def export_to_json(self, filepath: str, limit: int = None) -> int:
        """
        Export analysis history to JSON file.

        Args:
            filepath: Path to output JSON file
            limit: Maximum number of records to export (None for all)

        Returns:
            Number of records exported
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM analysis_history ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        records = []
        for row in rows:
            record = dict(row)
            # Parse JSON fields
            for json_field in ["soil_data", "analysis_params", "final_report", "executive_summary"]:
                if record.get(json_field):
                    try:
                        record[json_field] = json.loads(record[json_field])
                    except json.JSONDecodeError:
                        pass
            records.append(record)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        return len(records)

    def get_history_summary_th(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent analysis history with Thai summary.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of analysis records with Thai summaries
        """
        history = self.get_recent_history(limit)
        summaries = []

        for record in history:
            exec_summary = record.get("executive_summary", {})

            # Format timestamp to Thai-friendly format
            timestamp = record.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp)
                date_th = dt.strftime("%d/%m/%Y %H:%M")
            except (ValueError, TypeError):
                date_th = timestamp

            summary = {
                "id": record.get("id"),
                "date_th": date_th,
                "location_th": record.get("location_name", "ไม่ระบุ"),
                "crop_th": self._get_crop_name_th(record.get("crop_type", "")),
                "field_size_th": f"{record.get('field_size_rai', 0):.1f} ไร่",
                "status_th": exec_summary.get("overall_status_th", "ไม่ทราบ"),
                "score": record.get("overall_score", 0),
                "roi_percent": record.get("roi_percent", 0),
                "summary_th": exec_summary.get("bottom_line_th", "")
            }
            summaries.append(summary)

        return summaries

    def _get_crop_name_th(self, crop_type: str) -> str:
        """Get Thai name for crop type."""
        crop_names = {
            "Riceberry Rice": "ข้าวไรซ์เบอร์รี่",
            "Corn": "ข้าวโพด",
            "Rice": "ข้าว"
        }
        return crop_names.get(crop_type, crop_type)


# Singleton instance for easy access
_db_instance: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """Get the singleton database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


# Convenience functions
def save_analysis(
    location_name: str,
    crop_type: str,
    soil_data: Dict[str, Any],
    final_report: Dict[str, Any],
    **kwargs
) -> int:
    """Convenience function to save analysis."""
    return get_database().save_analysis(
        location_name=location_name,
        crop_type=crop_type,
        soil_data=soil_data,
        final_report=final_report,
        **kwargs
    )


def get_recent_history(limit: int = 5) -> List[Dict[str, Any]]:
    """Convenience function to get recent history."""
    return get_database().get_recent_history(limit)


def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """Convenience function to get analysis by ID."""
    return get_database().get_analysis_by_id(analysis_id)


def get_history_summary_th(limit: int = 5) -> List[Dict[str, Any]]:
    """Convenience function to get history with Thai summary."""
    return get_database().get_history_summary_th(limit)


def get_statistics() -> Dict[str, Any]:
    """Convenience function to get statistics."""
    return get_database().get_statistics()
