import json
import openai
from typing import List
import numpy as np
import os
import pickle
import logging
import random
import time

root_dir = os.path.dirname(os.path.abspath(__file__))
# 创建 logging 的文件路径
config_file = os.path.join(root_dir, '../config/llm.json')

logging_file = os.path.join(root_dir, '../logs/rest.log')

logging.basicConfig(filename=logging_file, level=logging.INFO, format='%(filename)s - %(asctime)s - %(message)s')

def get_llm_config(api_id):
    # 读取 JSON 文件
    with open(config_file, 'r', encoding='utf-8') as file:
        config_data = json.load(file)

    # 根据输入的 api_id 查找对应的配置对象
    api_config = None
    for item in config_data:
        if item['id'] == api_id:
            api_config = item['config']
            break

    if api_config is None:
        raise ValueError(f'No configuration found for api_id: {api_id}')

    key_path = os.path.join(root_dir, api_config['key_path'])
    # 读取 key_path 并获取 API 密钥
    with open(key_path, 'r', encoding='utf-8') as key_file:
        api_key = key_file.read().strip()

    # 获取其他配置信息
    api_config['api_key'] = api_key

    return api_config


def gpt_process(llm_config, prompt):
    openai.api_key = llm_config['api_key']
    openai.api_type = llm_config['api_type']
    openai.api_base = llm_config['api_base']
    openai.api_version = llm_config['api_version']
    response = openai.ChatCompletion.create(
            engine= llm_config['engine'],
            # replace this value with the deployment name you chose when you deployed the associated model.
            messages=[{"role": "user","content": prompt}],
            temperature=0,
            max_tokens= llm_config['max_token'],
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)

    text = response.choices[0].message.content.strip()

    return text


def gpt_process_loops(llm_config, prompt, loop_number):
    processed_time = 0
    while processed_time < loop_number:
        try:
            # 发送请求给 GPT-4 API
            response_text = gpt_process(llm_config, prompt)
            processed_time = loop_number
            return response_text
        except Exception as e:
            logging.error(f"Error: {e}")
            random_number = random.uniform(1, 2)
            seconds = int(random_number * llm_config["interval"])
            time.sleep(seconds)
            processed_time += 1

    return None

def get_embedding(question_text, llm_config):
    # 设置 OpenAI API 密钥
    openai.api_key = llm_config['api_key']
    openai.api_type = llm_config['api_type']
    openai.api_base = llm_config['api_base']
    openai.api_version = llm_config['api_version']

    response = openai.Embedding.create(input=[question_text], engine=llm_config['engine'])
    embedding_list: List = response['data'][0]['embedding']
    embedding_array = np.array(embedding_list)
    return embedding_array


def load_single_dict_file(path):
    all_dicts = []

    with open(path, "rb") as f:
        while True:
            try:
                loaded_dict = pickle.load(f)
                all_dicts.append(loaded_dict)
            except EOFError:
                break

    # 将所有加载的字典合并为一个字典
    merged_dict = {}
    for d in all_dicts:
        merged_dict.update(d)

    return merged_dict