"""
S.O.I.L.E.R. Base Agent
Abstract base class for all specialized agents with Thai language support.
"""

import sys
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class AgentProcessResponse:
    """Simple response wrapper for agent process results."""

    def __init__(self, success: bool, payload: Dict[str, Any], error_message: Optional[str] = None):
        self.success = success
        self.payload = payload
        self.error_message = error_message


class BaseAgent(ABC):
    """
    Abstract base class for all S.O.I.L.E.R. agents.

    All agents output observations in Thai language (except technical terms N, P, K, pH, ROI).

    Provides common functionality including:
    - Standardized logging with agent identification
    - Processing pipeline with timing
    - Thai language observations for agent chain
    """

    def __init__(self, agent_name: str, agent_name_th: str = "", verbose: bool = True):
        """
        Initialize the base agent.

        Args:
            agent_name: English identifier for this agent
            agent_name_th: Thai name for display
            verbose: Whether to print logs to console
        """
        self.agent_name = agent_name
        self.agent_name_th = agent_name_th or agent_name
        self.verbose = verbose
        self._processing_start: Optional[datetime] = None
        self._observation_th: str = ""

    def think(self, message: str) -> None:
        """Log agent's thinking process."""
        if self.verbose:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] [{self.agent_name}] INFO: {message}", file=sys.stderr)

    def log_action(self, action: str) -> None:
        """Log an action being performed."""
        if self.verbose:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] [{self.agent_name}] DEBUG: {action}", file=sys.stderr)

    def log_result(self, result: str) -> None:
        """Log a result or finding."""
        if self.verbose:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] [{self.agent_name}] INFO: {result}", file=sys.stderr)

    def log_warning(self, warning: str) -> None:
        """Log a warning."""
        if self.verbose:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] [{self.agent_name}] WARNING: {warning}", file=sys.stderr)

    def log_error(self, error: str) -> None:
        """Log an error."""
        if self.verbose:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] [{self.agent_name}] ERROR: {error}", file=sys.stderr)

    def set_observation_th(self, observation: str) -> None:
        """Set Thai observation for the next agent."""
        self._observation_th = observation

    def _start_processing(self) -> None:
        """Mark the start of processing."""
        self._processing_start = datetime.now()

    def _end_processing(self) -> float:
        """Mark the end of processing and return duration."""
        if self._processing_start:
            return (datetime.now() - self._processing_start).total_seconds()
        return 0.0

    @abstractmethod
    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core execution logic to be implemented by each agent.
        All observations must be in Thai language.

        Args:
            input_data: Agent-specific input data

        Returns:
            Agent-specific output data with 'observation_th' key
        """
        pass

    def process(self, input_data: Dict[str, Any]) -> AgentProcessResponse:
        """
        Main processing pipeline for the agent.

        Args:
            input_data: Input data for processing

        Returns:
            AgentProcessResponse with success status and payload
        """
        self._start_processing()

        try:
            result = self._execute(input_data)

            # Ensure Thai observation exists
            if "observation_th" not in result:
                result["observation_th"] = self._observation_th or f"{self.agent_name_th}: การวิเคราะห์เสร็จสมบูรณ์"

            result["agent_name"] = self.agent_name
            result["agent_name_th"] = self.agent_name_th
            result["processing_time_sec"] = self._end_processing()

            return AgentProcessResponse(success=True, payload=result)

        except Exception as e:
            self.log_error(f"เกิดข้อผิดพลาด: {str(e)}")
            error_payload = {
                "error": str(e),
                "agent_name": self.agent_name,
                "agent_name_th": self.agent_name_th,
                "observation_th": f"เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}",
                "processing_time_sec": self._end_processing()
            }
            return AgentProcessResponse(success=False, payload=error_payload, error_message=str(e))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.agent_name}', th='{self.agent_name_th}')>"
