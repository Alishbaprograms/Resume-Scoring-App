import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from dotenv import load_dotenv
from pdf2image import convert_from_path
import time

load_dotenv()

endpoint = os.getenv("AZURE_CV_ENDPOINT")
key = os.getenv("AZURE_CV_KEY")

client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))


def extract_text_with_azure(pdf_path, output_txt_path, temp_img_dir="temp/azure_ocr_imgs"):
    os.makedirs(temp_img_dir, exist_ok=True)
    pages = convert_from_path(pdf_path)
    final_text = ""

    for idx, page in enumerate(pages):
        img_path = os.path.join(temp_img_dir, f"{os.path.basename(pdf_path)}_page{idx}.jpg")
        page.save(img_path)

        with open(img_path, "rb") as image_stream:
            read_response = client.read_in_stream(image_stream, raw=True)

        operation_location = read_response.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        while True:
            result = client.get_read_result(operation_id)
            if result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)

        if result.status == OperationStatusCodes.succeeded:
            for page_result in result.analyze_result.read_results:
                for line in page_result.lines:
                    final_text += line.text + "\n"

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    return final_text
