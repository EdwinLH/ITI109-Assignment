from dotenv import load_dotenv
import os

# Import namespaces
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

def main():
    try:
        # Get Configuration Settings
        load_dotenv()
        prediction_endpoint = os.getenv('CLASSIFICATION_ENDPOINT')
        prediction_key = os.getenv('CLASSIFICATION_KEY')
        project_id = os.getenv('PROJECTID')
        model_name = os.getenv('MODELNAME')
        
        # Create client using endpoint and key
        credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
        prediction_client = CustomVisionPredictionClient(endpoint=prediction_endpoint, credentials=credentials)

        # Classify test images
        for image in os.listdir('Test-Images'):
            
            image_data = open(os.path.join('Test-Images',image), "rb").read()
            results = prediction_client.classify_image(project_id, model_name, image_data)

            # Loop over each label prediction and print any with probability > 50%
            for prediction in results.predictions:
                if prediction.probability > 0.5:
                    print(image, ': {} ({:.0%})'.format(prediction.tag_name, prediction.probability))
    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()