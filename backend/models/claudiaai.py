"""
Claudia AI - Financial Assistant
Provides personalized financial news and assistance based on user preferences
"""
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to find utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from utils.gemini_utils import call_gemini


def claudiai(user_description: str, chat_history: List[Dict[str, Any]], system_request: str, language: str = "en") -> Dict[str, Any]:
    """
    Claudia AI - Financial Assistant
    
    Args:
        user_description (str): User's description/interests from onboarding
        chat_history (List[Dict]): Array of chat messages with 'role' and 'content' keys
        system_request (str): Type of request - 'introduction', 'response', or 'daily_intro'
        language (str): Language code - 'en' for English, 'id' for Indonesian
    
    Returns:
        Dict: Response with success status and AI message
    """
    
    try:
        # Get current date for context
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Map language codes to full language names
        language_map = {
            "en": "English",
            "id": "Indonesian (Bahasa Indonesia)"
        }
        
        target_language = language_map.get(language, "English")
        
        if system_request == "introduction":
            prompt = f"""You are Claudia AI, a friendly and knowledgeable financial assistant for BeritaBank. 
            
            User Profile: {user_description}
            Current Date: {current_date}
            
            This is the first interaction with a new user. Your task is to:
            1. Give a warm, professional introduction as Claudia AI
            2. Acknowledge their interests/description: "{user_description}"
            3. Ask 2-3 clarifying questions to better understand their financial interests and needs
            4. Explain how you can help them with financial news, market updates, and personalized advice
            
            Keep the tone conversational, helpful, and professional. Ask questions that will help you provide better personalized financial assistance.
            
            IMPORTANT: Respond in {target_language} only. Do not provide translations or multiple languages."""
            
        elif system_request == "response":
            if not chat_history:
                return {
                    'success': False,
                    'error': 'No chat history provided for response'
                }
            
            # Get the latest user message
            latest_message = None
            for message in reversed(chat_history):
                if message.get('role') == 'user':
                    latest_message = message.get('content', '')
                    break
            
            if not latest_message:
                return {
                    'success': False,
                    'error': 'No user message found in chat history'
                }
            
            # Build context from chat history
            chat_context = ""
            for msg in chat_history[-5:]:  # Last 5 messages for context
                role = msg.get('role', '')
                content = msg.get('content', '')
                if role == 'user':
                    chat_context += f"User: {content}\n"
                elif role == 'assistant':
                    chat_context += f"Claudia: {content}\n"
            
            prompt = f"""You are Claudia AI, a financial assistant for BeritaBank.
            
            User Profile: {user_description}
            Current Date: {current_date}
            
            Recent Chat Context:
            {chat_context}
            
            Latest User Question: "{latest_message}"
            
            Please provide a helpful, accurate response to the user's latest question. 
            Consider their interests and previous conversation context.
            
            Guidelines:
            - Provide relevant financial information, news, or advice
            - If discussing specific investments, include appropriate disclaimers
            - Be conversational and helpful
            - Reference their interests when relevant
            - If you need to search for current information, mention that you're providing general guidance
            
            IMPORTANT: Respond in {target_language} only. Do not provide translations or multiple languages."""
            
        elif system_request == "daily_intro":
            prompt = f"""You are Claudia AI, a financial assistant for BeritaBank.
            
            User Profile: {user_description}
            Current Date: {current_date}
            
            This is a daily check-in message. Your task is to:
            1. Greet the user warmly
            2. Provide relevant daily financial updates based on their interests: "{user_description}"
            3. Give brief market insights or news that might interest them
            4. Offer to help with any specific questions they might have
            
            Chat History Context:
            {_format_chat_history(chat_history)}
            
            Guidelines:
            - Keep it concise but informative
            - Focus on areas that match their interests
            - Mention general market trends, not specific investment advice
            - Be encouraging and supportive
            - End with an invitation for them to ask questions
            
            IMPORTANT: Respond in {target_language} only. Do not provide translations or multiple languages."""
            
        else:
            return {
                'success': False,
                'error': f'Invalid system_request type: {system_request}. Must be "introduction", "response", or "daily_intro"'
            }
        
        # Call Gemini API
        response = call_gemini(
            prompt=prompt,
            model="gemini-1.5-pro",
            temperature=0.7,  # Slightly more creative for conversational AI
            google_search_retrieval=True  # Enable web search for current information
        )
        
        if response.startswith("Error:"):
            return {
                'success': False,
                'error': response
            }
        
        return {
            'success': True,
            'message': response.strip(),
            'timestamp': datetime.now().isoformat(),
            'type': system_request
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Claudia AI error: {str(e)}'
        }


def _format_chat_history(chat_history: List[Dict[str, Any]]) -> str:
    """Helper function to format chat history for context"""
    if not chat_history:
        return "No previous conversation history."
    
    formatted = ""
    for msg in chat_history[-10:]:  # Last 10 messages
        role = msg.get('role', '')
        content = msg.get('content', '')
        if role == 'user':
            formatted += f"User: {content}\n"
        elif role == 'assistant':
            formatted += f"Claudia: {content}\n"
    
    return formatted.strip()


# Example usage and testing
if __name__ == "__main__":
    # Test introduction
    print("Testing Introduction:")
    result = claudiai(
        user_description="Interested in cryptocurrency and banking news",
        chat_history=[],
        system_request="introduction"
    )
    print(result)
    
    # Test response
    print("\nTesting Response:")
    result = claudiai(
        user_description="Interested in cryptocurrency and banking news",
        chat_history=[
            {"role": "user", "content": "What's the current state of Bitcoin?"},
            {"role": "assistant", "content": "Bitcoin has been showing some volatility recently..."}
        ],
        system_request="response"
    )
    print(result)
    
    # Test daily intro
    print("\nTesting Daily Intro:")
    result = claudiai(
        user_description="Interested in cryptocurrency and banking news",
        chat_history=[
            {"role": "user", "content": "Tell me about market trends"},
            {"role": "assistant", "content": "The market has been showing mixed signals..."}
        ],
        system_request="daily_intro"
    )
    print(result)
