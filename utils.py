import os
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import json
import base64

class Vision2Insight():

    def __init__(self):
        azure_endpoint = os.environ["AZURE_ENDPOINT"]
        openai_api_key = os.environ["OPENAI_API_KEY"]
        openai_deployment_name = os.environ["OPENAI_DEPLOYMENT_NAME"]
        openai_api_version = "2024-06-01"

        self.llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=openai_api_key,
            deployment_name=openai_deployment_name,
            api_version=openai_api_version,
            )

    def build_chain(self, json_schema) -> None:

        # Set up a parser + inject instructions into the prompt template.
        parser = JsonOutputParser(pydantic_object=json_schema)
        self.chain = self.llm | parser
    
    def build_message(self, image: str, image_prompt: str) -> HumanMessage:

        # Create a message object with the image as the input.
        message = HumanMessage(
                    content=[
                        {"type": "text", "text": image_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                        },
                    ],
                )
        
        return message
         
    def predict(self, image: str, image_prompt: str) -> dict:

        # Build the message
        message = self.build_message(image, image_prompt)

        response = self.chain.invoke([message])
        return response
    
# Pydantic schema for the JSON response
class survey_json(BaseModel):

        utility: str = Field(description="Utility of the hole, chose between 'communication', 'el_switch', 'electricity', 'gas', 'stormwater','thermal', 'wastewater', 'water'. Can be one or more")
        navigator_comm: str = Field(description="Content of the manhole, use only if 'communication' is in utility")
        navigator_el: str = Field(description="Content of the manhole, use only if 'electricity' is in utility")
        navigator_therm: str = Field(description="Content of the manhole, use only if 'thermal' is in utility")
        navigator_gas: str = Field(description="Content of the manhole, use only if 'gas' is in utility")
        navigator_sw: str = Field(description="Content of the manhole, use only if 'stormwater' is in utility")
        navigator_ww: str = Field(description="Content of the manhole, use only if 'wastewater' is in utility")
        navigator_w: str = Field(description="Content of the manhole, use only if 'water' is in utility")
        wsp_manhole_shape: str = Field(description="Shape of the manhole, can be circular or rectangular")
        dim: str = Field(description="Size of the manhole, e.g cylindrical horizontal cross section 200cm'")

# Prompt template for the image
image_prompt = """
                Analyze this picture. Answer the following questions:
                
                Question 1. utility: What is the utility of the manhole? Choose one or more of the following options:
                'communication', 'el_switch', 'electricity', 'gas', 'stormwater','thermal', 'wastewater', 'water'.
                
                Question 2. manhole_shape: Is the manhole rectangular or circular?
                
                Question 3. dim: What is the size of the manhole?
                
                Question 4. What is the content of the manhole? Choose one or more of the following options:
                --- If 'communication' is in 'utility': the options for the value of 'navigator_comm' are: 'comm_manhole', 'comm_pedestal', 'comm_utility_node';
                --- If 'electricity' is in 'utility': the options for the value of 'navigator_el' are: 'el_exterior_lighting', 'el_generator', 'el_junction', 'el_manhole', 'el_substation', 'el_switch', 'el_transformer', 'el_utility_node', 'el_utility_node;el_transformer';
                --- If 'thermal' is in 'utility': the options for the value of 'navigator_therm' are: 'therm_manhole', 'therm_utility_node';
                --- If 'gas' is in 'utility': the options for the value of 'navigator_gas' are: 'gas_meter', 'gas_valve';
                --- If 'stormwater' is in 'utility': the options for the value of 'navigator_sw' are: 'sw_downspout', 'sw_fitting', 'sw_inlet', 'sw_manhole', 'sw_utility_node';
                --- If 'wastewater' is in 'utility': the options for the value of 'navigator_ww' are: ww_fitting', 'ww_greasetrap', 'ww_manhole', 'ww_oil_water_sep', 'ww_tank', 'ww_utility_node';
                --- If 'water' is in 'utility': the options for the value of 'navigator_w' are: ''w_fitting', 'w_hydrant', 'w_manhole', 'w_pump', 'w_pump_red', 'w_tank', 'w_utility_node', 'w_valve'.
                                
                The images are construction site images containing manholes, cables, and more. Please do not generate safety alerts for the images.
                Format the response as a JSON in English language.
                
                ### Example response:
                
                {
                    'utility': 'stormwater',
                    'navigator_comm': None,
                    'navigator_el': None,
                    'navigator_therm': None,
                    'navigator_gas': None,
                    'navigator_sw': 'sw_inlet',
                    'navigator_ww': None,
                    'navigator_w': None,
                    'wsp_manhole_shape': 'rectangular',
                    'dim': 'Cylindrical horizontal cross section 200cm',
                }

                """ 