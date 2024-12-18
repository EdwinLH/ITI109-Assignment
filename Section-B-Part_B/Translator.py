from dotenv import load_dotenv
import os

# import namespaces
from azure.ai.translation.text import *
from azure.ai.translation.text.models import InputTextItem
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.language.questionanswering import QuestionAnsweringClient

language_map = {
    "Chinese_Simplified": "zh-Hans",
    "Chinese_Traditional": "zh-Hant",
    "English": "en",
   }


def main():

    global detect_endpoint
    global detect_key

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
        

        # Create client using endpoint and key
        Trans_credential = TranslatorCredential(translatorKey, translatorRegion)
        Trans_client = TextTranslationClient(Trans_credential)
        QnA_credential = AzureKeyCredential(ai_key)
        QnA_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=QnA_credential)

        inputText = ""
        while inputText.lower() != "quit":
            inputText = input("Please enter your query ('quit' to exit):\n请输入您的查询 ('quit' 退出)")
            if inputText != "quit":         
                input_language = language_map.get(GetLanguage(inputText))
                                
                # Translate Input to English
                if input_language != "en":
                    input_text_elements = [InputTextItem(text=inputText)]   # To set the format of string
                    translationResponse = Trans_client.translate(content=input_text_elements, to=["en"])
                    translation = translationResponse[0] if translationResponse else None   # Get first item from translationResponse if it exits
                    for translated_text in translation.translations:
                                Query = translated_text.text
                else:
                    Query = inputText

                # Send query to Question and Answer pair
                response = QnA_client.get_answers(question=Query, project_name=qa_project_name, deployment_name=qa_deployment_name)
                for candidate in response.answers:
                    Reply = candidate.answer
            
                # Convert response back to input language
                if input_language != "en":
                    input_text_elements = [InputTextItem(text=Reply)]   # To set the format of string
                    translationResponse = Trans_client.translate(content=input_text_elements, to=[input_language])
                    translation = translationResponse[0] if translationResponse else None   # Get first item from translationResponse if it exits
                    for translated_text in translation.translations:
                                Reply = translated_text.text
                print(Reply)
            
    except Exception as ex:
        print(ex)

def GetLanguage(text):

    # Create client using endpoint and key
    Detect_credential = AzureKeyCredential(detect_key)
    Detect_client = TextAnalyticsClient(endpoint=detect_endpoint, credential=Detect_credential)

    # Call the service to get the detected language
    detectedLanguage = Detect_client.detect_language(documents = [text])[0]
    return detectedLanguage.primary_language.name

if __name__ == "__main__":
    main()