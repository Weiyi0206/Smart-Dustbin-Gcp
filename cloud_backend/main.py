import functions_framework
from google.cloud import firestore
import vertexai
from vertexai.generative_models import GenerativeModel, Part

PROJECT_ID = os.environ.get("GCP_PROJECT_ID") 
LOCATION = os.environ.get("GCP_LOCATION", "us-central1") 

try:
    db = firestore.Client()
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel("gemini-2.5-flash")
    
except Exception as e:
    print(f"Init Error: {e}")

@functions_framework.http
def process_waste(request):
    """
    Receives an image file, asks Gemini AI to classify it,
    saves the result to Firestore, and returns a command.
    """
    
    # 1. CORS Headers (Allows your browser/dashboard to talk to this function)
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # 2. Check if a file was uploaded
    if 'file' not in request.files:
        return ({'error': 'No file uploaded'}, 400, {'Access-Control-Allow-Origin': '*'})
    
    file = request.files['file']
    content = file.read()
    
    try:
        # 3. Ask Gemini AI to classify the image
        # We create an image object from the uploaded file
        image_part = Part.from_data(data=content, mime_type="image/jpeg")
        
        prompt = """
        Analyze this image. Classify it into EXACTLY one of these 12 categories:
        [battery, biological, brown-glass, cardboard, clothes, green-glass, metal, paper, plastic, shoes, trash, white-glass].
        Return ONLY the category name in lowercase. Do not write sentences.
        """
        
        # Call the AI model
        response = model.generate_content([image_part, prompt])
        detected_class = response.text.strip().lower()
        
        # 4. Determine Bin Logic (Recycle vs General)
        # We define what counts as recyclable
        recyclable_items = ['cardboard', 'paper', 'metal', 'plastic', 'brown-glass', 'white-glass', 'green-glass', 'clothes', 'shoes']
        
        if detected_class in recyclable_items:
            bin_type = "Recycle"
        else:
            bin_type = "General"

        # 5. Save the data to Firestore (The Database)
        # This allows the dashboard to see the history
        db.collection('waste_logs').add({
            'timestamp': firestore.SERVER_TIMESTAMP,
            'class': detected_class,
            'bin': bin_type,
            'device_id': 'feather-s3-simulation'
        })

        # 6. Send the command back to the (simulated) device
        return ({
            "status": "success",
            "class": detected_class,
            "bin": bin_type,
            "command": "OPEN_" + bin_type.upper() # e.g., OPEN_RECYCLE
        }, 200, {'Access-Control-Allow-Origin': '*'})

    except Exception as e:
        print(f"Error: {e}")
        return ({'error': str(e)}, 500, {'Access-Control-Allow-Origin': '*'})