from dotenv import load_dotenv
import os

# import namespaces
from azure.ai.translation.text import *
from azure.ai.translation.text.models import InputTextItem
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.language.questionanswering import QuestionAnsweringClient
import azure.cognitiveservices.speech as speech_sdk
from playsound import playsound

language_map = {
    "Chinese_Simplified": "zh-Hans",
    "Chinese_Traditional": "zh-Hant",
    "English": "en",
   }


def main():

    global detect_endpoint
    global detect_key
    global translatorKey
    global translatorRegion
    global speech_key
    global speech_region
    global speech_config

    try:
        # Get Configuration Settings
        load_dotenv()
        translatorRegion = os.getenv('TRANSLATOR_REGION')
        translatorKey = os.getenv('TRANSLATOR_KEY')
        detect_endpoint = os.getenv('DETECT_ENDPOINT')
        detect_key = os.getenv('DETECT_KEY')
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')
        qa_project_name = os.getenv('QA_PROJECT_NAME')
        qa_deployment_name = os.getenv('QA_DEPLOYMENT_NAME')
        speech_key = os.getenv('SPEECH_KEY')
        speech_region = os.getenv('SPEECH_REGION')
        

        # Create client using endpoint and key
        QnA_credential = AzureKeyCredential(ai_key)
        QnA_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=QnA_credential)
        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(speech_key, speech_region)
     
        inputText = ""
        
        while inputText.lower() != "quit":
            inputText = input("Welcome to Frozenhot chatbot (Enter 'speech' to speak, 'text' to type, 'quit' to exit):\n")
            
            if inputText == "speech":
                while inputText.lower() != "main":
                    inputText = input("In speech mode now, 'main' to return\n") 
                    
                    # Configure speech service
                    #speech_config = speech_sdk.SpeechConfig(speech_key, speech_region)
                    print('Ready to use speech service in:', speech_config.region)

                    # Get spoken input
                    command = TranscribeCommand()
                    print(command)
                
                            
            elif inputText == "text":
            
                while inputText.lower() != "main":
                    inputText = input("In text mode now, 'main' to return\n")
            
            elif inputText != "quit":
                 print("Please select the mode")
           
    except Exception as ex:
        print(ex)

def GetLanguage(text):

    # Create client using endpoint and key
    Detect_credential = AzureKeyCredential(detect_key)
    Detect_client = TextAnalyticsClient(endpoint=detect_endpoint, credential=Detect_credential)

    # Call the service to get the detected language
    detectedLanguage = Detect_client.detect_language(documents = [text])[0]
    return detectedLanguage.primary_language.name


def Translator(input_language, output_language, TransIn):
    
    # Create client using endpoint and key 
    Trans_credential = TranslatorCredential(translatorKey, translatorRegion)
    Trans_client = TextTranslationClient(Trans_credential)

     # Translate Input if user's language is not English
    if input_language != "en":
        input_text_elements = [InputTextItem(text=TransIn)]   # To set the format of string
        translationResponse = Trans_client.translate(content=input_text_elements, to=[output_language])
        translation = translationResponse[0] if translationResponse else None   # Get first item from translationResponse if it exits
        for translated_text in translation.translations:
                    TransOut = translated_text.text
    else:
        TransOut = TransIn
    return TransOut


def TranscribeCommand():
    command = ''

    # Configure speech recognition
    current_dir = os.getcwd()
    audioFile = current_dir + '\\1.mp3'
    print(audioFile)
    playsound(audioFile)
    audio_config = speech_sdk.AudioConfig(filename=audioFile)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
       
    # Process speech input
    speech = speech_recognizer.recognize_once_async().get()
    command = speech.text
    print(command)
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        print(command)
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)

    # Return the command
    return command


if __name__ == "__main__":
    main()