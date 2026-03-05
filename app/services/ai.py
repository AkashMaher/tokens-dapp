import json
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Dict, Any
from app.models.token import Insight, ModelInfo
from logging import getLogger

load_dotenv()


class AIGeneration:
    """Service to generate AI insights for token data using multiple AI models. for now we are using groq"""

    def __init__(self, model: str = "groq"):
        self.default_model = model
        self.clients = {
            "groq": OpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
            )
        }
        
        self.logger = getLogger("AIGeneration")

    def get_client(self, model_name: str = None) -> OpenAI:
        if model_name not in self.clients:
            model_name = model_name or self.default_model
            if model_name not in self.clients:
                raise ValueError(f"Unsupported AI model: {model_name}")
        return self.clients[model_name]

    def build_prompt(self, token_data: Dict[str, Any]) -> str:
        """Build structured prompt with token data."""
        return f"""
        You are a crypto market analyst. Analyze the following token data and provide a concise insight. You may get historical data with days_ago field if you need to analyze trends. if historical data is not present, focus on current market data. need correct context to analyze the market trends, risks, or opportunities.
        Token Data:
        {json.dumps(token_data, indent=2)}

        Respond with valid JSON only (no extra text):
        {{
            "reasoning": "A 1-2 sentence reasoning on market trends, risks, or opportunities based on the data.",
            "sentiment": "Bullish|Bearish|Neutral"
        }}

        Ensure sentiment is one of: Bullish (positive outlook), Bearish (negative), Neutral (balanced).
        """

    async def generate_insight(
        self, token_data: Dict[str, Any], provider="groq", model="llama-3.1-8b-instant"
    ) -> tuple[dict[str, str], dict[str, str]]:
        """Call Groq, parse, and validate response."""
        prompt = self.build_prompt(token_data)

        try:
            client = self.get_client(provider)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty AI response")

            insight_dict = json.loads(content)

            if "reasoning" not in insight_dict or "sentiment" not in insight_dict:
                raise ValueError("Missing required fields in AI response")

            validated_insight = Insight(
                reasoning=insight_dict["reasoning"], sentiment=insight_dict["sentiment"]
            )

            model_info = ModelInfo(provider=provider, model=model)
            
            self.logger.info(f"AI insight generated successfully with model {model} from provider {provider}")

            return validated_insight.model_dump(), model_info.model_dump()

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error from AI response: {str(e)}. Response content: {content if 'content' in locals() else 'N/A'}")
            raise ValueError(f"Invalid JSON from AI: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error during AI insight generation: {str(e)}. Response content: {content if 'content' in locals() else 'N/A'}")
            raise ValueError(
                f"AI call failed: {str(e)}. Response content: {content if 'content' in locals() else 'N/A'}"
            )
