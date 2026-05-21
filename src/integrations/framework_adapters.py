"""
SAP Integration for Popular AI Frameworks
Supports: OpenAI, Hugging Face, Local LLMs (Ollama, LM Studio)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from src.core.sap_engine import SovereignAlignmentProtocol, ValidationResult


class AIFrameworkAdapter(ABC):
    """Base adapter for AI framework integration"""
    
    def __init__(self, sap_engine: SovereignAlignmentProtocol):
        self.sap = sap_engine
    
    @abstractmethod
    def validate_before_response(self, prompt: str, generated_response: str) -> ValidationResult:
        """Validate AI response before returning to user"""
        pass


class OpenAIAdapter(AIFrameworkAdapter):
    """Integration for OpenAI API"""
    
    def __init__(self, sap_engine: SovereignAlignmentProtocol, api_key: str = None):
        super().__init__(sap_engine)
        self.api_key = api_key
        self.framework_name = "OpenAI"
    
    def validate_before_response(self, prompt: str, generated_response: str) -> ValidationResult:
        """
        Intercept OpenAI response and validate through SAP
        """
        context = {
            "framework": self.framework_name,
            "prompt_length": len(prompt),
            "response_length": len(generated_response),
            "request_type": "chat_completion"
        }
        
        result = self.sap.validate_action(
            action=generated_response,
            context=context,
            actor_role="assistant",
            target_user_role="user"
        )
        
        return result
    
    def create_wrapped_client(self):
        """
        Returns a wrapper around OpenAI client with SAP validation
        Usage:
            client = adapter.create_wrapped_client()
            response = client.chat.completions.create(...)  # Auto-validated
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            original_create = client.chat.completions.create
            
            def validated_create(*args, **kwargs):
                # Call original
                response = original_create(*args, **kwargs)
                content = response.choices[0].message.content
                
                # Validate through SAP
                result = self.validate_before_response(
                    prompt=kwargs.get('messages', [{}])[-1].get('content', ''),
                    generated_response=content
                )
                
                if not result.is_approved:
                    # Return sanitized message
                    response.choices[0].message.content = (
                        f"[Content blocked by ethical guardrail] {result.message}"
                    )
                
                return response
            
            client.chat.completions.create = validated_create
            return client
            
        except ImportError:
            raise ImportError("openai library required. Install: pip install openai")


class HuggingFaceAdapter(AIFrameworkAdapter):
    """Integration for Hugging Face Models"""
    
    def __init__(self, sap_engine: SovereignAlignmentProtocol, model_name: str = None):
        super().__init__(sap_engine)
        self.model_name = model_name or "meta-llama/Llama-2-7b-chat"
        self.framework_name = "HuggingFace"
    
    def validate_before_response(self, prompt: str, generated_response: str) -> ValidationResult:
        """Validate HF model output"""
        context = {
            "framework": self.framework_name,
            "model": self.model_name,
            "prompt_length": len(prompt),
            "response_length": len(generated_response)
        }
        
        return self.sap.validate_action(
            action=generated_response,
            context=context,
            actor_role="assistant",
            target_user_role="user"
        )
    
    def create_validated_pipeline(self):
        """
        Create a validated text generation pipeline
        Usage:
            pipe = adapter.create_validated_pipeline()
            result = pipe("What is AI?", max_length=100)
        """
        try:
            from transformers import pipeline
            
            pipe = pipeline(
                "text-generation",
                model=self.model_name,
                device=0  # GPU
            )
            
            def validated_generate(prompt: str, **kwargs):
                response = pipe(prompt, **kwargs)
                generated_text = response[0]['generated_text']
                
                # Validate
                result = self.validate_before_response(prompt, generated_text)
                
                if not result.is_approved:
                    return [{
                        'generated_text': f'[Content blocked] {result.message}'
                    }]
                
                return response
            
            return validated_generate
            
        except ImportError:
            raise ImportError("transformers library required. Install: pip install transformers")


class LocalLLMAdapter(AIFrameworkAdapter):
    """Integration for Local LLMs (Ollama, LM Studio, etc.)"""
    
    def __init__(
        self,
        sap_engine: SovereignAlignmentProtocol,
        base_url: str = "http://localhost:11434",
        model_name: str = "llama2"
    ):
        super().__init__(sap_engine)
        self.base_url = base_url
        self.model_name = model_name
        self.framework_name = "LocalLLM"
    
    def validate_before_response(self, prompt: str, generated_response: str) -> ValidationResult:
        """Validate local LLM output"""
        context = {
            "framework": self.framework_name,
            "model": self.model_name,
            "base_url": self.base_url,
            "prompt_length": len(prompt)
        }
        
        return self.sap.validate_action(
            action=generated_response,
            context=context,
            actor_role="assistant",
            target_user_role="user"
        )
    
    def generate_with_validation(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate from local LLM with SAP validation
        Usage:
            response = adapter.generate_with_validation("What is ethics?")
        """
        import requests
        
        try:
            # Call local LLM
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs
                }
            )
            
            response.raise_for_status()
            data = response.json()
            generated = data.get('response', '')
            
            # Validate
            result = self.validate_before_response(prompt, generated)
            
            return {
                "prompt": prompt,
                "generated": generated,
                "approved": result.is_approved,
                "status_code": result.status_code,
                "violations": [v.__dict__ for v in result.violations],
                "message": result.message
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "error": f"Cannot connect to local LLM at {self.base_url}",
                "hint": "Make sure Ollama or LM Studio is running"
            }


class SAPMiddleware:
    """
    Middleware for integrating SAP with web frameworks
    (Flask, FastAPI, etc.)
    """
    
    def __init__(self, sap_engine: SovereignAlignmentProtocol):
        self.sap = sap_engine
        self.validation_stats = {
            "total_requests": 0,
            "blocked_count": 0,
            "approval_rate": 0.0
        }
    
    def validate_response(self, response_text: str, request_context: Dict = None) -> bool:
        """
        Validate response before sending to client
        Returns: True if approved, False if blocked
        """
        self.validation_stats["total_requests"] += 1
        
        result = self.sap.validate_action(
            action=response_text,
            context=request_context or {}
        )
        
        if not result.is_approved:
            self.validation_stats["blocked_count"] += 1
        
        # Update approval rate
        total = self.validation_stats["total_requests"]
        blocked = self.validation_stats["blocked_count"]
        self.validation_stats["approval_rate"] = (
            ((total - blocked) / total * 100) if total > 0 else 0
        )
        
        return result.is_approved
    
    def get_stats(self) -> Dict:
        """Return validation statistics"""
        return self.validation_stats
