from django.http import HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
import json
from openai import AzureOpenAI
from requests_html import HTMLSession
import time
import random


def get_authorization(request):
    try:
        if request.method == 'POST':
            bearer_token = request.headers.get('authorization')
            split_token = bearer_token.split(' ')[1].split(';')

            return {
                "API_KEY": split_token[0],
                "ENDPOINT": split_token[1],
                "PHOTO_API_KEY": split_token[2],
                "PHOTO_API_ENDPOINT": split_token[3]
            }
        else:
            return None

    except:
        return None


def authorization_failed_message():
    return Response({"error": "Invalid api key or endpoint"}, status=401)


# Create your views here.
# Get sources
@api_view(['POST'])
def get_sources(request):
    authorization = get_authorization(request)
    if not authorization:
        return authorization_failed_message()

    target = request.data.get('target')
    environment = request.data.get('environment')
    user = request.data.get('user')
    record = request.data.get('record')
    print(target, environment, user, record)

    # Call Azure OpenAI GPT-4 API
    headers = {
        "Content-Type": "application/json",
        "api-key": authorization["API_KEY"],
    }

    template_prompt = f"""
        You are a professional product designer, you are expert in creating professional metaphorical products that convey complex ideas in an engaging and understandable way. You should think out-of-box and give innovative ideas. 
        The source should have association with the target in a reasonable and novel way. Make the source concrete, do not mention the target in the source name
        Generate a list of sources
        You'll think step by step:
        1. Analyze the target's structures (e.g., body, lid, handle) across sensory levels (vision—shape, dimension, material, color, smell, taste, touch, sound,  ), and its functions and interactions.
        Example: 
        Body: A cylindrical, cream-colored stainless steel kettle with a smooth, cool surface and an insulating layer.
        Lid: Flat and slightly domed, fitting securely on the body, blending seamlessly with a soft click when closed.
        Handle: Curved and arching over the top, featuring a non-slip grip, comfortable to hold, and slightly warm after use.
        Functions：Boil Water, Keep Water Warm, Filter, Boiling Indicator; 
        Behaviors: Grab the handle, tilt the kettle, and shake if necessary to pour.
        
        2. Analyze the target's context (reflective level), including what {user} concerned about when using it, and how will it influence their self-esteem and thoughts. Analyze the semantic meaning when using the target in the {environment}.
        Example:
        Users aged 20-25 are attracted to kettles that reflect current design trends like minimalism, or retro styles, and offering customization options can enhance personal expression. A design that encourages social media interaction, such as sharing tea or coffee routines, can appeal to their desire for social connection and status affirmation. In a living room setting, the kettle may symbolize warmth and hospitality, seamlessly integrating into the space. 
         
        3. Based on the target's properties, generate novel and surprising sources that is rare but reasonable. Consider how the design triggers emotions, playful or fun, enhances usability, conveys symbolic meaning, promote a value. Balance object similarity and category dissimilarity.
        Example source for fire hydrant in a kindergarten: elephant(elephant nose shapes like the handle of the fire hydrant. Also elephant uses its nose to pump water)
        
        4. give detail and inspiring description of the design(whithin 200 words),think from these things, make your final explanation into 2 sentences: Potential Using Scenarios; Emotional Impact & Meaning of the new scenario ; Origin of the symbol words/customs; Some possible integration of Source and Target
        
        There is a Record containing the proposed sources. Please do not duplicate these.
        Generate a list of sources(10 sources) for product design in the following structured format, considering the environment and user of the product:
        !don't reply other words except the json itself
        [
            {{
                "name": "Source Name(only the specific name, like tree instead of tree of knowledge, like hourglass instead of hourglass illumination)",
                "description": "A brief description of the source",
                "details": "Detailed explanation of the connection between target and source",
                "source_type": "Types of connection between target and source.(Choose from visceral, behavioral and reflective)"
            }},
            ...
        ]

        Target: {target}
        Environment: {environment}
        User: {user}
        Record: {record}
    """

    # Payload for the request
    payload = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a product designer who in good at use metaphor in design."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": template_prompt
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 1500
    }

    # Send request
    try:
        response = requests.post(authorization['ENDPOINT'], headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

    # Handle the response as needed
    content_str = response.json()['choices'][0]['message']['content']

    # 去除Markdown代码块符号
    if content_str.startswith('```json'):
        content_str = content_str.strip('```json\n')
    if content_str.endswith('```'):
        content_str = content_str.strip('\n```')
    print(content_str)

    # 尝试将字符串解析为字典或列表
    try:
        content = json.loads(content_str)
    except json.JSONDecodeError:
        print(Response({"error": "Failed to parse content as JSON"}, status=400))

    # 将API响应中的内容转化为Source对象并保存到数据库（如果需要）
    sources = []
    for item in content:
        sources.append({
            "name": item['name'],
            "description": item['description'],
            "details": item['details'],
            "source_type": item['source_type']
        })

    response_data = {
        "source": sources,
    }
    return Response(response_data)


# Get attributes of selected source
@api_view(['POST'])
def get_attributes(request):
    authorization = get_authorization(request)
    if not authorization:
        return authorization_failed_message()

    target_name = request.data.get('target_name')
    source_name = request.data.get('source_name')
    connection = request.data.get('connection')
    target_img_url = request.data.get('target_img_url')
    source_img_url = request.data.get('source_img_url')

    # Call Azure OpenAI GPT-4 API
    headers = {
        "Content-Type": "application/json",
        "api-key": authorization['API_KEY'],
    }

    template_prompt = f"""
      Metaphor is an important method in product design.
      Before design, it's crucial to analyze the target and the source, including their interaction, function, and form.
      Please analyze the {target_name} (target) and {source_name} (source) considering the fact that {connection}(their connection) and generate relevant attributes(9 for target and 9 for source) . 
      Analysis should refer to the target picture and source picture and be consistent with the pictures. At the same time, you should focus on the target or source of the image, rather than the background. The attributes should be common to this type of object, rather than specific to this image.
      Considering their structures (e.g., body, lid, handle), sensory levels (vision, touch, sound, etc.), functions, and interactions. Follow these steps:
      
    A. Multi-sensory Analysis in both target and source. Try each category has at least one idea
    Vision: Shape, color, material, dimensions, size, graphics,light and shadow. Example: Target's Body: A cylindrical, cream-colored kettle with an insulating layer. 20 cm height.
    Usage: Functions, interactions, movement. Example: Target's Lids： Boil Water, Keep Water Warm, Filter, shake when the water is boiled.
    Touch: Surface texture, weight, temperature,material. Example: Target's Body: smooth, cool surface.
    Sound: Example: the cick sound of Opening/closing, .
    Smell: Associated scents.
    Taste: Relevant flavors, if applicable.
    !Be care: Each of the six categories (Vision, Usage, Touch, Sound, Smell, Taste) has at least one idea
   
    B. Summarize:
    Format your answers in fewer than 6 words.
    Description should be less than 2 sentences. Be creative and inspiring.
    Example: Cylindrical body, cream-colored body, stainless steel
      
      reply in the following structured format:
      must have the 'Flag'!
      don't reply other words except the json itself
      [
          {{
              "content": "Attribute Content",
              "attribute_type": "Type of the attribute (Choose only from Vision, Usage, Touch, Sound, Smell, Taste)",
              "Flag": "1"  # 1 indicates this is an attribute of the target; 2 indicates this is an attribute of the source
          }},
          ...
      ]

      Target: {target_name}
      Source: {source_name}
      Connection: {connection}
    """

    # Payload for the request
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a product designer who in good at analyzing the product and designing metaphor design."
            },
            {
                "role": "user",
                "content": template_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": target_img_url
                        }
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": source_img_url
                        }
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 1000
    }

    # Send request
    try:
        response = requests.post(authorization['ENDPOINT'], headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

    # Handle the response as needed (e.g., print or process)
    content_str = response.json()['choices'][0]['message']['content']
    print("Content string:", repr(content_str))
    print(type(content_str))

    # 去除Markdown代码块符号
    if content_str.startswith('```json'):
        content_str = content_str.strip('```json\n')
    if content_str.endswith('```'):
        content_str = content_str.strip('\n```')

    # 尝试将字符串解析为字典或列表
    try:
        content = json.loads(content_str)
        print("success")
    except json.JSONDecodeError:
        print("something went wrong")

    # 将API响应中的内容转化为Source对象并保存到数据库（如果需要）
    target_attributes = []
    source_attributes = []
    for item in content:
        if item['Flag']=="1":
            target_attributes.append(
                {
                    "content": item['content'],
                    "attribute_type": item['attribute_type'],
                }
            )
        else:
            source_attributes.append(
                {
                    "content": item['content'],
                    "attribute_type": item['attribute_type'],
                }
            )

    print(target_attributes)
    print(source_attributes)

    mapping = generate_mainmapping(target_attributes, source_attributes, target_name, source_name, connection, authorization)
    print(mapping)

    # 准备返回的数据
    response_data = {
        "target_attributes": [{"content": attr['content'], "attribute_type": attr['attribute_type']} for attr in
                              target_attributes],
        "source_attributes": [{"content": attr['content'], "attribute_type": attr['attribute_type']} for attr in
                              source_attributes],
        "mapping": mapping
    }
    print(response_data)

    return Response(response_data)


def generate_mainmapping(target_attributes, source_attributes, target_name, source_name, connection, authorization):
    mappings = []

    mapping_prompt = f"""
    You are a product designer skilled in metaphorical design.
    Your task is to create main mappings between the following target and source attributes:

    Target: {target_name}
    Source: {source_name}
    Connection: {connection}

    Target Attributes:
    {json.dumps([{"content": attr['content'], "attribute_type": attr['attribute_type']} for attr in target_attributes], indent=2)}

    Source Attributes:
    {json.dumps([{"content": attr['content'], "attribute_type": attr['attribute_type']} for attr in source_attributes], indent=2)}

    you think step by step:
    1. in target and source, Multi-sensory Analysis in target and source,
        Vision: Shape, color, material, dimensions, size, graphics,light and shadow. Example: Target's Body: A cylindrical, cream-colored kettle with an insulating layer. 20 cm height.
        Usage: Functions, interactions, movement. Example: Target's Lids： Boil Water, Keep Water Warm, Filter, shake when the water is boiled.
        Touch: Surface texture, weight, temperature,material. Example: Target's Body: smooth, cool surface.
    2. Summarize:
        target_attribute and source_attribute fewer than 6 words, exclude the target and source names; Example: Cylindrical body, cream-colored body, stainless steel
        description should be less than 2 sentences.be creative and inspiring.

    Please generate 2 mappings in the following format:
    Do not include any additional text other than the JSON.
    
    [
        {{
            "target_attribute": "Target Attribute Content",
            "target_type": "Type of the target attribute",
            "source_attribute": "Source Attribute Content",
            "source_type": "Type of the source attribute",
            "description": "Short description of why these attributes are paired."
        }},
        {{
            "target_attribute": "Target Attribute Content",
            "target_type": "Type of the target attribute",
            "source_attribute": "Source Attribute Content",
            "source_type": "Type of the source attribute",
            "description": "Short description of why these attributes are paired."
        }}
    ]
    """

    # 调用 GPT 生成主映射
    headers = {
        "Content-Type": "application/json",
        "api-key": authorization['API_KEY'],
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": mapping_prompt
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }

    try:
        response = requests.post(authorization['ENDPOINT'], headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to generate main mapping. Error: {e}"}

    mapping_content = response.json()['choices'][0]['message']['content']

    # 去除Markdown代码块符号
    if mapping_content.startswith('```json'):
        mapping_content = mapping_content.strip('```json\n')
    if mapping_content.endswith('```'):
        mapping_content = mapping_content.strip('\n```')
    print(mapping_content)

    try:
        generated_mappings = json.loads(mapping_content)
    except (json.JSONDecodeError, KeyError) as e:
        return {"error": "Failed to parse GPT response as JSON."}

    # 保存映射
    for mapping in generated_mappings:
        mappings.append({
            "target_attribute": mapping['target_attribute'],
            "target_type": mapping['target_type'],
            "source_attribute": mapping['source_attribute'],
            "source_type": mapping['source_type'],
            "description": mapping['description']
        })

    return mappings


# Generate idea based on selected attributes
@api_view(['POST'])
def push_custom_mapping(request):
    authorization = get_authorization(request)
    if not authorization:
        return authorization_failed_message()

    try:
        print("Raw Body:", request.body)
        print("Parsed JSON:", json.loads(request.body))
    except json.JSONDecodeError as e:
        return HttpResponseBadRequest(f"Invalid JSON: {e}")

    target_name = request.data.get('target_name')
    source_name = request.data.get('source_name')
    target_attribute = request.data.get('target_attribute')
    source_attribute = request.data.get('source_attribute')
    connection = request.data.get('connection')
    print(target_name, source_name, target_attribute, source_attribute, connection)

    # Call Azure OpenAI GPT-4 API
    headers = {
        "Content-Type": "application/json",
        "api-key": authorization['API_KEY'],
    }

    template_prompt = f"""
      Based on the metaphor design approach, let's combine the attributes of the target and the source to generate a creative idea.
      Consider the following:
      - Target: {target_name}
      - Source: {source_name}
      - Connection: {connection}
      - Target Attribute: {target_attribute}
      - Source Attribute: {source_attribute}

      Please describe a creative idea or concept that effectively merges the {target_attribute} of the {target_name} with the {source_attribute} of the {source_name}.
      The idea should be practical and relevant to product design, highlighting how the target and source attributes work together.
      Provide the description that: 
      1. detail explain how these two attributes are practically integrated into the product design, focusing on the implementation.
      2. explain the meaning and emotion this design triggered
      3. within 2 sentences 70 words
      Example description content: The lamp's leaf-shaped lampshade filters warm light through small openings, creating a dappled sunlight effect. This design brings a calming, natural ambiance into the home.
      
      Must in the following structured json-like format:
      {{
          "description": "Generated idea description that combines the selected attributes."
      }}
      
      Do not include any additional text other than the JSON.
    """

    # Payload for the request
    payload = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a creative product designer with expertise in metaphor-based design thinking."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": template_prompt
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 400
    }

    # Send request
    try:
        response = requests.post(authorization['ENDPOINT'], headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        return Response({"error": f"Failed to make the request. Error: {e}"}, status=500)

    # Handle the response as needed (e.g., print or process)
    content_str = response.json()['choices'][0]['message']['content']

    # 去除Markdown代码块符号
    if content_str.startswith('```json'):
        content_str = content_str.strip('```json\n')
    if content_str.endswith('```'):
        content_str = content_str.strip('\n```')
    print(content_str)

    # 尝试将字符串解析为字典或列表
    try:
        content = json.loads(content_str)
    except json.JSONDecodeError:
        return Response({"error": "Failed to parse the response from the API."}, status=500)

    # 准备返回的数据
    response_data = {
        "target_attribute": target_attribute,
        "source_attribute": source_attribute,
        "description": content.get('description', 'No description generated')
    }

    return Response(response_data)


# Get constraint
@api_view(['POST'])
def get_constraint(request):
    authorization = get_authorization(request)
    if not authorization:
        return authorization_failed_message()

    target_name = request.data.get('target_name')
    source_name = request.data.get('source_name')
    target_attribute = request.data.get('target_attribute')
    source_attribute = request.data.get('source_attribute')
    target_image_url = request.data.get('target_image_url')
    source_image_url = request.data.get('source_image_url')
    print(target_image_url, source_image_url)

    # 构建 GPT 的 prompt，要求生成结构化输出
    prompt = f"""
        You are a visual analyst specialized in product design. 
        You will analyze the provided images and generate structured outputs.

        - Target: {target_name}
        - Source: {source_name}
        
        For the target image, please generate 11 constraints (requirements for design). each category at least 1 idea
        -Structure: Components, dimensions, materials (e.g., lid, handle, plug, 40 cm height, double-layered, hollow).
        -Function: Higher or low-level purpose (e.g., body boils water, lid filters tea leaves, Filter collects dust), avoid too abstract words like "visual appeal".
        -Behavior: Mechanical actions (e.g., Unscrew the lid, control panel adjusts temperature, Scrape).
        
        For the source image, please generate 11 properties (characteristics or features). try to keep each category at least 1 idea
        -Vision: Shape, structure, color, material, dimensions, size, graphics, light and shadow. Example: A cylindrical, cream-colored kettle with an insulating layer. 20 cm height. another example: A long nose, big ears, Thick limbs, blunt, rough skins.
        -Usage: Functions, interactions, movement. Example: Boil Water, Keep Water Warm, Filter, shake when the water is boiled. another example: Provide shelter for bees, protect bees, store honey, reflect division of labor
        -Touch: Surface texture, weight, temperature,material. Example: smooth, cool surface.
        -Sound: Example: the cick sound of Opening/closing. if no, skip it.
        -Smell: Associated scents. if no, skip it.
        -Taste: Relevant flavors. if no, skip it.
        
        Must in the following JSON format:
        [
            {{
                "content": "Description of the constraint of target(within 5 words, exclude the target and source names)",
                "constraint_type": "Type of the constraint (Choose from Function, Behavior, Structure)"
            }},
            ...
            {{
                "content": "Description of the property of source(within 5 words, exclude the target and source names)",
                "property_type": "Type of the property (Choose from Vision, Usage, Touch, Sound, Smell, Taste)"
            }},
            ...
        ]
        
        don't reply other words except the json itself
        """

    # 构建请求的 payload
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that helps people analyze images for product design."
            },
            {
                "role": "user",
                "content": prompt  # 确保这是一个字符串
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": target_image_url  # 正确的字典格式，包含 "url" 键
                        }
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": source_image_url  # 正确的字典格式，包含 "url" 键
                        }
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 1200
    }

    # 发送请求到 GPT API
    try:
        response = requests.post(authorization['ENDPOINT'], headers={"Content-Type": "application/json", "api-key": authorization['API_KEY']},
                                 json=payload)
        response.raise_for_status()  # 如果HTTP请求返回状态码非200，则抛出异常
    except requests.RequestException as e:
        return Response({"error": f"Failed to analyze images. Error: {e}"}, status=500)

    # 处理 API 响应
    result = response.json()['choices'][0]['message']['content']

    # 去除Markdown代码块符号
    if result.startswith('```json'):
        result = result.strip('```json\n')
    if result.endswith('```'):
        result = result.strip('\n```')
    print(result)
    try:
        generated_data = json.loads(result)
        print(generated_data)
    except (json.JSONDecodeError, KeyError) as e:
        return Response({"error": "Failed to parse GPT response as JSON."}, status=500)

    # 返回结构化的约束和性质数据
    return Response(generated_data)


# Generate results
@api_view(['POST'])
def generate_results(request):
    authorization = get_authorization(request)
    if not authorization:
        return authorization_failed_message()

    # 从请求中获取数据
    target = request.data.get('target')
    source = request.data.get('source')
    constraint = request.data.get('constraint')
    property = request.data.get('property')
    target_attribute = request.data.get('target_attribute')
    source_attribute = request.data.get('source_attribute')

    """if not all([constraint, property, target_attribute, source_attribute]):
        return Response({"error": "Missing required fields."}, status=400)"""

    # 构建 GPT 的 prompt，生成多个设计简介
    prompt = f"""
        You are a product designer tasked with creating new product designs using metaphor. The design target is {target}, and the source is {source}.
        
        First of all, the design must focus on the following mapping:
        - Target Attribute: {target_attribute}
        map to
        - Source Attribute: {source_attribute}
        
        Additionally, the product should incorporate the following constraint: "{constraint}", and utilize the following property from the source: "{property}".

        Please generate four distinct design descriptions, each with a unique style. 
        You think step by step:
        Conceptualize 4 distinct meanings, emotions, and corresponding design styles based on the provided information. Consider different approaches such as playful, elegant, modern, minimalist, poetic, humorous, Memphis-style, Nendo-style, Alessi-style, etc.
        -As for 'description', up to 200 words that includes:
        --a Using scenario; 
        --Metaphor expression, integrating the source's attributes through multi-sensory angles, such as behavioral, vision, smell, sound, touch. Vary the implicit and explicit metaphorical expressions across the four designs;    
        --Meaning and Emotion, How the design transforms the meaning of the target product and what emotions it conveys.
        -As for 'imageprompt', it's for Dalle3 to generate the high-quality product picture. up to 300 words that includes:
        --copy all content of 'description'(scenario, metaphor expression, meaning and emotion)
        --considering constaints and property
        --merge them together detailed and concise, considering other things that are needed in generating a product picture, avoid banned words
        --Avoid vague descriptions of materials, such as durable materials, which are difficult to reflect during the generate picture process. Make everything as visual as possible.
        --The product design needs to be product-level, considering manufacture requirements
        
        Ensure that each of the four design descriptions is as diverse as possible by exploring different meanings, interaction styles, and design aesthetics. 
        
        The descriptions should be returned in the following JSON format:
        [
            {{
                "name": "name of the product",
                "slogan": "a short description of the product",
                "descriptions": "content of detail description. Use line break '\n' to separate Using scenario, Metaphor expression, Meaning and Emotion so that front-end users can read more easily.",
                "imageprompt": "a prompt for dalle3 to generate the product picture"
            }},
            ...
        ]
        
        don't reply other words except the json itself
        """

    # 调用 GPT 生成设计简介
    headers = {
        "Content-Type": "application/json",
        "api-key": authorization["API_KEY"],
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 1600
    }

    try:
        response = requests.post(authorization['ENDPOINT'], headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to generate main mapping. Error: {e}"}

    content = response.json()['choices'][0]['message']['content']
    print(content)

    # 去除Markdown代码块符号
    if content.startswith('```json'):
        content = content.strip('```json\n')
    if content.endswith('```'):
        content = content.strip('\n```')

    gpt_response = json.loads(content)
    print(gpt_response)

    return Response(gpt_response)


# Generate final picture
@api_view(['POST'])
def generate_pic(request):
    authorization = get_authorization(request)
    if not authorization:
        return authorization_failed_message()

    # 从请求中获取数据
    prompt = request.data.get('prompt')
    #print(prompt)

    client = AzureOpenAI(
        api_version="2024-02-01",
        azure_endpoint=authorization["ENDPOINT"],
        api_key=authorization["API_KEY"],
    )

    t = random.randint(0, 3000)
    print(t)
    t0 = t / 1000
    time.sleep(t0)

    try:
        result = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1  # 生成一张图片
        )

        # 解析返回的 JSON 并获取图像 URL
        image_url = json.loads(result.model_dump_json())['data'][0]['url']
        #print(image_url)
        return Response({"image_url": image_url})

    except Exception as e:
        #print(f"Error generating image: {e}")
        return Response({"error": f"Error generating image: {e}"})


def search_photo(keyword, authorization):
    # 预定义的关键词和对应的图片URL
    predefined_photos = {
        "Toothpick": "https://m.media-amazon.com/images/I/71dy1tplvEL.__AC_SX300_SY300_QL70_FMwebp_.jpg",
        "Alarm Clock": "https://m.media-amazon.com/images/I/71BXosF6dQL.__AC_SX300_SY300_QL70_FMwebp_.jpg",
        "Dessert Stand": "https://m.media-amazon.com/images/I/71eossMQi8L._AC_SX679_.jpg",
        "Kitchen box": "https://m.media-amazon.com/images/I/71ZtMqgEr4L._AC_SX679_.jpg",
        "Table Lamp": "https://images.pexels.com/photos/1112598/pexels-photo-1112598.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    }

    # 检查关键词是否在预定义的列表中
    if keyword in predefined_photos:
        print(f"Using predefined photo URL for keyword: {keyword}")
        return predefined_photos[keyword]

    # 如果关键词不在预定义的列表中，则调用 API 进行搜索
    print(keyword)
    # 定义请求的URL和参数
    url = f"{authorization['PHOTO_API_ENDPOINT']}?query={keyword}&per_page=2"

    # 创建一个 HTML 会话
    session = HTMLSession()

    # 设置请求头以模拟浏览器
    headers = {
        "Authorization": authorization['PHOTO_API_KEY'],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    t = random.randint(0, 3000)
    print(t)
    t0 = t / 1000
    time.sleep(t0)

    # 发送 GET 请求
    response = session.get(url, headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        # 解析响应的JSON数据
        data = response.json()
        # 获取照片列表
        photos = data.get("photos", [])

        # 如果有照片，返回第一张照片的URL
        if photos:
            i = random.randint(0, len(photos) - 1)
            photo_url = photos[i].get("src", {}).get("tiny", None)
            #photo_url = f"{photo_url}?auto=compress&cs=tinysrgb&w=800"
            print(f"Found photo URL: {photo_url}")
            return photo_url
        else:
            print("No photos found for the given keyword.")
            return None
    else:
        print(f"Failed to fetch photos. Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        return None



