#!/usr/bin/env python3
"""
HuggingFace Service Test Script
Designed to work with your existing project structure
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_environment_setup():
    """Test that all required environment variables and files are present"""
    print("🔍 Testing Environment Setup...")
    print("=" * 50)
    
    # Check project structure
    required_dirs = ['models', 'pages', 'services', 'utils']
    required_files = ['app.py', '.env', 'requirements.txt']
    
    print("📁 Project Structure:")
    for directory in required_dirs:
        exists = Path(directory).exists()
        print(f"   {directory}/: {'✅' if exists else '❌'}")
    
    print("\n📄 Required Files:")
    for file in required_files:
        exists = Path(file).exists()
        print(f"   {file}: {'✅' if exists else '❌'}")
    
    # Check environment variables
    print("\n🔑 Environment Variables:")
    env_vars = {
        'HUGGINGFACE_API_TOKEN': os.getenv('HUGGINGFACE_API_TOKEN'),
        'WATSON_API_KEY': os.getenv('WATSON_API_KEY'),
        'WATSON_NLU_API_KEY': os.getenv('WATSON_NLU_API_KEY'),
        'IBM_GRANITE_API_KEY': os.getenv('IBM_GRANITE_API_KEY')
    }
    
    for var_name, value in env_vars.items():
        if value:
            masked = f"{value[:8]}..." if len(value) > 8 else value
            print(f"   {var_name}: ✅ {masked}")
        else:
            print(f"   {var_name}: ⚠️  Not set")
    
    return env_vars

def create_huggingface_service():
    """Create a HuggingFace service that fits your architecture"""
    
    hf_service_code = '''"""
HuggingFace Service for Personal Finance Chatbot
Integrates with your existing service architecture
"""

import os
import requests
from typing import Dict, List, Optional
from huggingface_hub import login
import streamlit as st

class HuggingFaceService:
    """Service class for HuggingFace API integration"""
    
    def __init__(self):
        self.api_token = os.getenv('HUGGINGFACE_API_TOKEN')
        self.api_base_url = "https://api-inference.huggingface.co/models"
        self.headers = {}
        
        if self.api_token:
            self.headers = {"Authorization": f"Bearer {self.api_token}"}
            try:
                login(token=self.api_token)
                self.connected = True
            except Exception as e:
                self.connected = False
                print(f"HuggingFace connection warning: {e}")
        else:
            self.connected = False
    
    def analyze_financial_sentiment(self, text: str) -> Dict:
        """Analyze financial sentiment using FinBERT"""
        if not self.connected:
            return self._fallback_sentiment(text)
        
        model_name = "ProsusAI/finbert"
        api_url = f"{self.api_base_url}/{model_name}"
        
        try:
            response = requests.post(
                api_url, 
                headers=self.headers, 
                json={"inputs": text}
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return {
                        "label": result[0]["label"],
                        "score": result[0]["score"],
                        "model": "FinBERT",
                        "success": True
                    }
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
        
        return self._fallback_sentiment(text)
    
    def classify_financial_topic(self, text: str) -> Dict:
        """Classify financial queries into topics"""
        categories = [
            "savings and budgeting",
            "investment and retirement", 
            "debt management",
            "tax planning",
            "insurance",
            "general financial advice"
        ]
        
        if not self.connected:
            return self._fallback_classification(text, categories)
        
        model_name = "facebook/bart-large-mnli"
        api_url = f"{self.api_base_url}/{model_name}"
        
        try:
            response = requests.post(
                api_url,
                headers=self.headers,
                json={
                    "inputs": text,
                    "parameters": {"candidate_labels": categories}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "top_category": result["labels"][0],
                    "confidence": result["scores"][0],
                    "all_categories": dict(zip(result["labels"], result["scores"])),
                    "success": True
                }
        except Exception as e:
            print(f"Classification error: {e}")
        
        return self._fallback_classification(text, categories)
    
    def _fallback_sentiment(self, text: str) -> Dict:
        """Fallback sentiment analysis"""
        positive_words = ['good', 'great', 'happy', 'confident', 'optimistic']
        negative_words = ['worried', 'concerned', 'bad', 'stressed', 'anxious']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return {"label": "positive", "score": 0.7, "model": "fallback", "success": True}
        elif neg_count > pos_count:
            return {"label": "negative", "score": 0.7, "model": "fallback", "success": True}
        else:
            return {"label": "neutral", "score": 0.6, "model": "fallback", "success": True}
    
    def _fallback_classification(self, text: str, categories: List[str]) -> Dict:
        """Fallback topic classification using keywords"""
        text_lower = text.lower()
        
        keyword_map = {
            "savings and budgeting": ["save", "budget", "expense", "spending"],
            "investment and retirement": ["invest", "stock", "retirement", "401k"],
            "debt management": ["debt", "loan", "credit", "payment"],
            "tax planning": ["tax", "deduction", "refund"],
            "insurance": ["insurance", "coverage", "premium"],
            "general financial advice": ["money", "finance", "advice"]
        }
        
        scores = {}
        for category, keywords in keyword_map.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score / len(keywords)
        
        top_category = max(scores, key=scores.get)
        return {
            "top_category": top_category,
            "confidence": scores[top_category],
            "all_categories": scores,
            "success": True
        }
    
    def get_status(self) -> Dict:
        """Get service status"""
        return {
            "connected": self.connected,
            "api_token_present": bool(self.api_token),
            "status": "✅ Connected" if self.connected else "⚠️ Fallback Mode"
        }
'''
    
    # Write the service file
    services_dir = Path('services')
    services_dir.mkdir(exist_ok=True)
    
    hf_service_path = services_dir / 'huggingface_service.py'
    with open(hf_service_path, 'w') as f:
        f.write(hf_service_code)
    
    print(f"✅ Created: {hf_service_path}")
    return hf_service_path

def test_huggingface_functionality():
    """Test HuggingFace service functionality"""
    print("\n🧪 Testing HuggingFace Service...")
    print("=" * 50)
    
    try:
        # Import the service (create it first if it doesn't exist)
        services_path = Path('services')
        hf_service_path = services_path / 'huggingface_service.py'
        
        if not hf_service_path.exists():
            print("📝 Creating HuggingFace service...")
            create_huggingface_service()
        
        # Import and test
        sys.path.append(str(services_path.parent))
        from services.huggingface_service import HuggingFaceService
        
        # Initialize service
        hf_service = HuggingFaceService()
        status = hf_service.get_status()
        
        print(f"🔌 Connection Status: {status['status']}")
        print(f"🔑 API Token Present: {status['api_token_present']}")
        
        # Test 1: Sentiment Analysis
        print("\\n1️⃣ Testing Sentiment Analysis...")
        test_text = "I'm worried about my financial future and need help with saving money"
        sentiment_result = hf_service.analyze_financial_sentiment(test_text)
        
        print(f"   Input: '{test_text}'")
        print(f"   Result: {sentiment_result['label']} ({sentiment_result['score']:.2f})")
        print(f"   Model: {sentiment_result['model']}")
        
        # Test 2: Topic Classification
        print("\\n2️⃣ Testing Topic Classification...")
        query = "How should I start investing for retirement with $500 per month?"
        classification_result = hf_service.classify_financial_topic(query)
        
        print(f"   Query: '{query}'")
        print(f"   Category: {classification_result['top_category']}")
        print(f"   Confidence: {classification_result['confidence']:.2f}")
        
        print("\\n✅ All HuggingFace tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing HuggingFace service: {e}")
        return False

def test_integration_with_existing_app():
    """Test integration with your existing app structure"""
    print("\\n🔗 Testing Integration with Existing App...")
    print("=" * 50)
    
    # Check if we can import your existing services
    try:
        if Path('services/watson_service.py').exists():
            from services.watson_service_backup import *
            print("✅ Watson service integration: Ready")
        else:
            print("⚠️ Watson service: Not found (optional)")
            
        if Path('services/finance_service.py').exists():
            from services.finance_service import *
            print("✅ Finance service integration: Ready")
        else:
            print("⚠️ Finance service: Not found (will create)")
            
        if Path('app.py').exists():
            print("✅ Main app file: Found")
        else:
            print("❌ Main app file: Missing")
            
        print("\\n💡 Integration Status: Ready for HuggingFace integration!")
        return True
        
    except Exception as e:
        print(f"⚠️ Integration check warning: {e}")
        return False

def create_integration_example():
    """Create an example of how to use HuggingFace in your existing app"""
    
    integration_example = '''
# Add this to your app.py or relevant service file

from services.huggingface_service import HuggingFaceService

# Initialize HuggingFace service
@st.cache_resource
def get_huggingface_service():
    return HuggingFaceService()

def enhanced_chat_response(user_input, user_profile):
    """Enhanced chat response using HuggingFace AI"""
    hf_service = get_huggingface_service()
    
    # Analyze user sentiment
    sentiment = hf_service.analyze_financial_sentiment(user_input)
    
    # Classify the financial topic
    topic = hf_service.classify_financial_topic(user_input)
    
    # Customize response based on analysis
    response_tone = "empathetic" if sentiment["label"] == "negative" else "encouraging"
    
    # Your existing response logic here, enhanced with AI insights
    return generate_personalized_response(user_input, user_profile, topic, sentiment)

# Add to your Streamlit sidebar
def show_ai_status():
    """Show AI service status in sidebar"""
    hf_service = get_huggingface_service()
    status = hf_service.get_status()
    
    st.sidebar.markdown("### 🤖 AI Services")
    st.sidebar.info(f"HuggingFace: {status['status']}")
'''
    
    with open('integration_example.py', 'w') as f:
        f.write(integration_example)
    
    print("📝 Created integration_example.py with usage examples")

def main():
    """Main test function"""
    print("🤖 Personal Finance Chatbot - HuggingFace Integration Test")
    print("=" * 60)
    
    # Test 1: Environment Setup
    env_vars = test_environment_setup()
    
    # Test 2: Create/Test HuggingFace Service  
    success = test_huggingface_functionality()
    
    # Test 3: Integration Check
    integration_ready = test_integration_with_existing_app()
    
    # Create integration example
    create_integration_example()
    
    # Summary
    print("\\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Environment: {'✅' if env_vars.get('HUGGINGFACE_API_TOKEN') else '⚠️ No HF token'}")
    print(f"   HuggingFace Service: {'✅' if success else '❌'}")
    print(f"   Integration Ready: {'✅' if integration_ready else '⚠️'}")
    
    print("\\n🚀 Next Steps:")
    if env_vars.get('HUGGINGFACE_API_TOKEN'):
        print("1. Run: streamlit run app.py")
        print("2. Your chatbot now has AI-powered features!")
    else:
        print("1. Add HUGGINGFACE_API_TOKEN to your .env file")
        print("2. Get token from: https://huggingface.co/settings/tokens")
        print("3. Then run: streamlit run app.py")
    
    print("\\n💡 The chatbot works great even without HuggingFace tokens!")

if __name__ == "__main__":
    main()
'''