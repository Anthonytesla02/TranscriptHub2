import os
import requests
import json

# Hardcoded credentials for simplicity
api_key = "nCmZyPuNmY8PfYzg8NyjAE8BpQQKAftB"
api_url = "https://api.mistral.ai/v1/chat/completions"

def get_chat_response(messages, transcript_content, model="mistral-large-latest"):
    """
    Get a response from the Mistral AI model based on user messages and transcript context.
    
    Args:
        messages: List of message objects with 'role' and 'content'
        transcript_content: The transcript text to use as context
        model: The Mistral model to use
        
    Returns:
        Response from the AI model
    """
    # Create system prompt with the transcript content as context
    system_prompt = f"""You are a helpful assistant that answers questions based on the YouTube transcript provided below.
Use this transcript as your knowledge base to provide accurate, relevant information.
If the answer cannot be found in the transcript, politely say so and suggest what might help.

TRANSCRIPT:
{transcript_content}

When responding:
1. Focus on information from the transcript
2. Be concise but comprehensive
3. Include timestamps [MM:SS] when referencing specific parts of the video
4. If the transcript doesn't contain the answer, be honest about it
"""
    
    # Format messages for Mistral API
    formatted_messages = [{"role": "system", "content": system_prompt}]
    
    # Add user messages
    for msg in messages:
        formatted_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Prepare the payload
    payload = {
        "model": model,
        "messages": formatted_messages
    }
    
    # Set headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Make the API request
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the response
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling Mistral AI API: {str(e)}")
        return f"Error: Unable to get a response from the AI model. {str(e)}"

def summarize_transcript(transcript_content, model="mistral-large-latest"):
    """
    Generate a concise summary of the transcript content.
    
    Args:
        transcript_content: The transcript text to summarize
        model: The Mistral model to use
        
    Returns:
        A summary of the transcript
    """
    # Create system prompt for summarization
    system_prompt = """You are a helpful assistant that creates concise, informative summaries of YouTube video transcripts.
Your task is to extract the main topics, key points, and important information from the transcript.
Structure your summary with bullet points highlighting the main sections of the video.
"""
    
    user_prompt = f"""Please summarize the following YouTube transcript in a clear, organized way:

{transcript_content}

Create a title for this content based on the transcript, and provide a 2-3 sentence overview followed by 
5-7 bullet points covering the key topics and main points discussed in the video.
"""
    
    # Prepare messages for API call
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # Prepare the payload
    payload = {
        "model": model,
        "messages": messages
    }
    
    # Set headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Make the API request
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the response
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling Mistral AI API: {str(e)}")
        return f"Error: Unable to summarize the transcript. {str(e)}"