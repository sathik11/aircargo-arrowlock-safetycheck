import json
import os,base64
from openai import AzureOpenAI

from dotenv import load_dotenv
#load_dotenv(dotenv_path='/home/sathik/code/sats/sats-cargo-belly/.env.local')
load_dotenv()

aoai_resource_name = os.getenv("AOAI_RESOURCE")
aoai_deployment_name = os.getenv("AOAI_GPT4_DEPLOYMENT")
aoai_api_version = "2024-02-15-preview"#os.getenv("AOAI_API_VERSION")
aoai_key = os.getenv("AOAI_KEY") 

aoai_creds = {"resource_name": aoai_resource_name, 
        "key": aoai_key, 
        "apiversion": aoai_api_version, 
        "deployment_name": aoai_deployment_name}

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def construct_message(system_prompt,user_prompt, imagelist):
    message = [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [
                {"type": "text", "text": user_prompt},
            ]}
        ]
    # if len(imagelist)>=2:
    if imagelist != []:
        # if len(imagelist) == 1 and user_prompt == "":
        #     message[1]["content"] = [{"type": "text", "text": "\n"}]
        #     message[1]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpg;base64,{imagelist[0]}"}})
        #     message[1]["content"].append({"type": "text", "text": "\n"})
        # else:  
        for i,img_bytes in enumerate(imagelist):
            if i == 1:
                user_text = "Closer look of locks. Scrutinize the area to ensure all locks are securely in place."
            else:
                user_text = "Pay attention to the locks highlighted by the boxes in green and provide your analysis."
            message[1]["content"].append(
                {"type": "image_url", "image_url": {"url": f"data:image/jpg;base64,{img_bytes}"}}
            )
            message[1]["content"].append(
                {"type": "text", "text": f"{user_text}\n"})
    # print(message)
    return message

def get_aoai_client(aoai_creds):
    aoai_res_name = aoai_creds["resource_name"]
    aoai_client = AzureOpenAI(
            azure_endpoint = f"https://{aoai_res_name}.openai.azure.com", 
            api_key = aoai_creds["key"],  
            api_version = aoai_creds["apiversion"]
            )
    return aoai_client

def send_to_openai(aoai_img_path='./uploads'):
    
    SYSTEM_PROMPT = open("./openai_prompt.txt", "r").read()
    USER_PROMPT = ""
    client = get_aoai_client(aoai_creds)
    
    all_imgs_list = []
    bbox_image = [file for file in os.listdir(aoai_img_path) if file.startswith(('bound'))][0]
    zoom_image = [file for file in os.listdir(aoai_img_path) if file.startswith(('cropped'))][0]
    all_imgs_list= [encode_image(f"{aoai_img_path}/{bbox_image}"),encode_image(f"{aoai_img_path}/{zoom_image}")]

    message = construct_message(SYSTEM_PROMPT,USER_PROMPT,all_imgs_list)
    # print(message)
    response = client.chat.completions.create(
        model = aoai_creds["deployment_name"],
        messages = message,
        temperature = 0.3,
        top_p = 0.95
    )
    result = response.choices[0].message.content
    result1 = result.replace("```",'')
    start_index = result1.index('{')
    json_data = json.loads(result1[start_index:])
    print(json_data)
    return json_data


# aoai_img_path='./uploads'
# send_to_openai(aoai_creds,aoai_img_path)