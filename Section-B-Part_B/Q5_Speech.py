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
        speech_config = speech_sdk.SpeechConfig(speech_key, speech_region)
     
        inputText = ""
        
        while inputText.lower() != "quit":
            inputText = input("Welcome to Frozenhot chatbot (Enter 'speech' to speak, 'text' to type, 'quit' to exit):\n")
            
            # Speech Module
            if inputText == "speech":
                while inputText.lower() != "main":
                    inputText = input("<Frozenhot> In speech mode now, press any key to speak or 'main' to return\n") 
                    if inputText.lower() != "main":
                        
                        print('<Frozenhot> Ready to use speech service in:', speech_config.region)

                        # Get spoken input
                        command = TranscribeCommand()
                        
                        # Detect output language
                        input_language = language_map.get(GetLanguage(command))
                        
                        # Call Translator to convert input to English
                        output_language = "en"
                        Query = Translator(input_language, output_language, command)
        
                        # Send query to Question and Answer pair
                        response = QnA_client.get_answers(question=Query, project_name=qa_project_name, deployment_name=qa_deployment_name)
                        for candidate in response.answers:
                            Answer = candidate.answer

                        # Call Translator to convert answer back to user's language
                        Reply = Translator(input_language, input_language, Answer)
                        
                        # Configure speech synthesis
                        speech_config.speech_synthesis_voice_name = "zh-CN-XiaoxiaoNeural"
                        speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

                        # Synthesize spoken output
                        speak = speech_synthesizer.speak_text_async(Reply).get()
                        if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
                            print(speak.reason)
                        
                        print("Frozenhot> ", Reply)
                            
            elif inputText == "text":
            
                # Text Module
                while inputText.lower() != "main":
                    inputText = input("<Frozenhot> In text mode now, Please enter your query or 'main' to return\n")
                    if inputText.lower() != "main":
                        input_language = language_map.get(GetLanguage(inputText))
                                        
                        # Call Translator to convert input to English
                        output_language = "en"
                        Query = Translator(input_language, output_language, inputText)
        
                        # Send query to Question and Answer pair
                        response = QnA_client.get_answers(question=Query, project_name=qa_project_name, deployment_name=qa_deployment_name)
                        for candidate in response.answers:
                            Answer = candidate.answer

                        # Call Translator to convert answer back to user's language
                        Reply = Translator(input_language, input_language, Answer)
                        print("<Frozenhot> ", Reply)

            # Quit Module
            elif inputText != "quit":
                 print("<Frozenhot> Please select the mode")
           
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
    audioFile = current_dir + '\\Sample2.wav'               # Switch between Sample1 (Eng) or Sample2 (Chinese)
    playsound(audioFile)
    audio_config = speech_sdk.AudioConfig(filename=audioFile)
    speech_config.speech_recognition_language = "zh-CN"
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
    
       
    # Process speech input
    speech = speech_recognizer.recognize_once_async().get()
    command = speech.text
    
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        print("<Frozenhot> Speech text: ", command)
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