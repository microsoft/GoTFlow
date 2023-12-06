import json
from src.utils.aoai import get_llm_config, gpt_process_loops

class Outline_Generator:
    def __init__(self, llm_string, loops=3, prompt_template_path="..\\data\\util_prompts\\ppt_outline.txt"):
        self.llm_config = get_llm_config(llm_string)
        self.loops = loops
        self.prompt_template_path = prompt_template_path

    def generate_outline_from_json(self, json_text):
        if not json_text:
            print("Error: There is no JSON text.")
            exit(0)

        # Load the JSON object
        data = json.loads(json_text)

        manu_script = []
        # Iterate over the slides
        for slide_number, slide_data in data.items():
            print(f"Read slide {int(slide_number) + 1}")

            # Check if the slide has a 'manuscript' key
            if 'manuscript' in slide_data:
                # Iterate over the 'manuscript' list
                for item in slide_data['manuscript']:
                    # Check the 'type' of the item
                    if item['type'] == 'title':
                        # It's a main point in the outline
                        #print(f"  {item['text']}")
                        manu_script.append(f"# {item['text']}")
                    elif item['type'] == 'subtitle':
                        # It's a subpoint in the outline
                        #print(f"    {item['text']}")
                        manu_script.append(f"## {item['text']}")
                    elif item['type'] == 'content':
                        # It's a detail under the subpoint
                        #print(f"      {item['text']}")
                        manu_script.append(f"### {item['text']}")

        manuscript_text = '\n'.join(manu_script)

        prompt_template = ""
        with open(self.prompt_template_path, 'r', encoding="utf-8") as file:
            prompt_template += file.read()

        prompt = prompt_template.replace("${manuscript}", manuscript_text)
        output = gpt_process_loops(self.llm_config, prompt, self.loops)
        print(output)
        return


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

json_text = ""
with open("../../output/output.json", 'r') as file:
    json_text = file.read()

outline_gen = Outline_Generator("llm_long")
outline_gen.generate_outline_from_json(json_text)