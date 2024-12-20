import azure.functions as func
import logging
from utils import *

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="multimodal_llm")
def multimodal_llm(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Parse JSON payload from the request
        req_body = req.get_json()
        
        image_data = req_body.get("image_data")
        
        v2i_model = Vision2Insight()
        v2i_model.build_chain(json_schema=survey_json)
        answer = v2i_model.predict(image_data, image_prompt)
        
        # Return the result as a JSON response
        return func.HttpResponse(
            body = json.dumps(answer), 
            status_code = 200, 
            mimetype = "application/json"
            )

    except ValueError:
        return func.HttpResponse("Invalid JSON payload.", status_code=400)
    
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse("Internal Server Error", status_code=500)
