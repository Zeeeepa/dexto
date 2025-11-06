"""Quality gate system for output validation and retry logic."""

from __future__ import annotations

import json
import re
from typing import Any, Optional

import jsonschema
from openai import AsyncOpenAI

from .schemas import AgentInstance, QualityGate, QualityGateResult, QualityGateType


class QualityGateSystem:
    """System for validating agent outputs with configurable gates."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize quality gate system."""
        self.client = AsyncOpenAI(api_key=api_key)
        self.validators = {
            QualityGateType.JSON_SCHEMA: self._validate_json_schema,
            QualityGateType.REGEX_MATCH: self._validate_regex,
            QualityGateType.LLM_VALIDATION: self._validate_with_llm,
            QualityGateType.CUSTOM_FUNCTION: self._validate_custom,
        }
    
    async def validate(
        self,
        gate: QualityGate,
        output: Any,
        agent: AgentInstance
    ) -> QualityGateResult:
        """Validate agent output against quality gate.
        
        Args:
            gate: Quality gate configuration
            output: Agent output to validate
            agent: Agent instance
            
        Returns:
            QualityGateResult with validation outcome
        """
        validator = self.validators.get(gate.gate_type)
        if not validator:
            raise ValueError(f"Unknown gate type: {gate.gate_type}")
        
        try:
            passed = await validator(gate, output)
            
            return QualityGateResult(
                gate_id=gate.gate_id,
                passed=passed,
                agent_id=agent.id,
                output=output
            )
        
        except Exception as e:
            return QualityGateResult(
                gate_id=gate.gate_id,
                passed=False,
                agent_id=agent.id,
                output=output,
                error=str(e)
            )
    
    async def _validate_json_schema(self, gate: QualityGate, output: Any) -> bool:
        """Validate output against JSON schema.
        
        Config format:
        {
            "schema": {
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        }
        """
        schema = gate.validation_config.get("schema")
        if not schema:
            raise ValueError("JSON schema validation requires 'schema' in config")
        
        # Convert output to dict if string
        if isinstance(output, str):
            try:
                output = json.loads(output)
            except json.JSONDecodeError:
                return False
        
        try:
            jsonschema.validate(instance=output, schema=schema)
            return True
        except jsonschema.ValidationError:
            return False
    
    async def _validate_regex(self, gate: QualityGate, output: Any) -> bool:
        """Validate output against regex pattern.
        
        Config format:
        {
            "pattern": "regex_pattern",
            "match_type": "search|match|fullmatch"  # default: search
        }
        """
        pattern = gate.validation_config.get("pattern")
        if not pattern:
            raise ValueError("Regex validation requires 'pattern' in config")
        
        output_str = str(output)
        match_type = gate.validation_config.get("match_type", "search")
        
        if match_type == "match":
            return bool(re.match(pattern, output_str))
        elif match_type == "fullmatch":
            return bool(re.fullmatch(pattern, output_str))
        else:  # search
            return bool(re.search(pattern, output_str))
    
    async def _validate_with_llm(self, gate: QualityGate, output: Any) -> bool:
        """Validate output using LLM judgment.
        
        Config format:
        {
            "criteria": "validation criteria description",
            "model": "gpt-4o-mini"  # optional
        }
        """
        criteria = gate.validation_config.get("criteria")
        if not criteria:
            raise ValueError("LLM validation requires 'criteria' in config")
        
        model = gate.validation_config.get("model", "gpt-4o-mini")
        
        prompt = f"""Validate the following output against these criteria:

Criteria: {criteria}

Output: {output}

Does the output meet the criteria? Respond with ONLY 'yes' or 'no'."""
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a quality validator. Respond only 'yes' or 'no'."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().lower()
        return result == "yes"
    
    async def _validate_custom(self, gate: QualityGate, output: Any) -> bool:
        """Validate using custom function.
        
        Config format:
        {
            "function": "module.path.to.function"
        }
        
        The function should accept (output: Any) -> bool
        """
        func_path = gate.validation_config.get("function")
        if not func_path:
            raise ValueError("Custom validation requires 'function' in config")
        
        # Import and call custom function
        module_path, func_name = func_path.rsplit(".", 1)
        
        try:
            import importlib
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            
            return await func(output) if asyncio.iscoroutinefunction(func) else func(output)
        
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to load custom validator: {e}")
    
    async def validate_with_retry(
        self,
        gate: QualityGate,
        output: Any,
        agent: AgentInstance,
        retry_func: Optional[callable] = None
    ) -> QualityGateResult:
        """Validate with automatic retry on failure.
        
        Args:
            gate: Quality gate
            output: Output to validate
            agent: Agent instance
            retry_func: Optional function to call for retry (should return new output)
            
        Returns:
            Final validation result
        """
        result = await self.validate(gate, output, agent)
        
        if not result.passed and gate.retry_on_fail and retry_func:
            for attempt in range(gate.max_retries):
                # Retry agent execution
                new_output = await retry_func()
                result = await self.validate(gate, new_output, agent)
                result.retry_attempted = True
                
                if result.passed:
                    break
        
        return result

