import requests
import os
from dotenv import load_dotenv
from typing import Optional



load_dotenv()
api_key = os.getenv("LEMONFOX_API_KEY")



text = "Hello, how are you? . How's your wife ?"




def text_to_speech(
    text: str,
    api_key: str,
    output_file: str = "speech.mp3",
    voice: str = "sarah",
    response_format: str = "mp3"
    ):
        """
        Convert text to speech using Lemonfox API.

        :param text: Text to convert into speech
        :param api_key: Your Lemonfox API key
        :param output_file: Output audio file name
        :param voice: Voice name (default: sarah)
        :param response_format: Audio format (default: mp3)
        """

        url = "https://api.lemonfox.ai/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "input": text,
            "voice": voice,
            "response_format": response_format
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"Audio saved as {output_file}")
        else:
            raise Exception(f"Request failed: {response.status_code} - {response.text}")





# text_to_speech(
#     text=text,
#     api_key=api_key,
#     output_file="speech.mp3"
# )










def speech_to_text(
    api_key: str,
    audio_url: Optional[str] = None,
    audio_file_path: Optional[str] = None,
    language: str = "english",
    response_format: str = "json"
    ):
        """
        Convert speech to text using Lemonfox API.

        :param api_key: Lemonfox API key
        :param audio_url: Public URL of the audio file
        :param audio_file_path: Local path to audio file
        :param language: Language of the audio
        :param response_format: Response format (default: json)
        :return: Transcription response as dict
        """

        if not audio_url and not audio_file_path:
            raise ValueError("Either audio_url or audio_file_path must be provided")

        url = "https://api.lemonfox.ai/v1/audio/transcriptions"

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "language": language,
            "response_format": response_format
        }

        files = None

        # Case 1: URL-based audio
        if audio_url:
            data["file"] = audio_url

        # Case 2: Local file upload
        if audio_file_path:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"File not found: {audio_file_path}")

            files = {
                "file": open(audio_file_path, "rb")
            }

        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files
        )

        if files:
            files["file"].close()

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed: {response.status_code} - {response.text}")


result = speech_to_text(
    api_key=api_key,
    audio_file_path="speech.mp3"
)

# print(result)




