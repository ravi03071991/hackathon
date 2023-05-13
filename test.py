import ast
import os
import sys
import json
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
import openai as oai


oai.api_key = os.getenv("OPENAI_API_KEY")


IS_MOCK = False
IS_DEBUG = True
#if IS_DEBUG:
#  result0 = { "type": "fiction",                                       
#              "audience": "experienced-reader" }  


env = Environment(loader=FileSystemLoader("prompts/"))
env.lstrip_blocks = True
env.trim_blocks = True


def test_jee(prompt, question):
  prompt = prompt + question
  completion = oai.ChatCompletion.create(model="gpt-3.5-turbo",
                                         messages = [{"role":"user", "content":prompt}],
                                         temperature = 0.3,
                                         top_p = 1, n=1, max_tokens=400)
  print(completion.choices[0].message.content)


def call_openai(prompt, max_tokens=100, temp=0.3):
  completion = oai.ChatCompletion.create(model="gpt-3.5-turbo", messages = [{"role":"user", "content":prompt}],
                                           temperature = temp, top_p = 1, n=1, max_tokens=max_tokens)
  #print(completion.choices[0].message.content)
  return(completion.choices[0].message.content)


def print_debug(prompt, prompt_idx=0):
    print("PROMPT", str(prompt_idx))
    print("---------------------")
    print(prompt)


def select_subtopics(subtopics=None, concepts=None, subtopic0_tmp = "subtopics0.txt"):
  ''' Given subtopics and concepts, from concepts figure out which all subtopics the 
      student is weak in'''
  with open("concepts.json", 'r') as f:
    concepts = json.load(f)

  prompt0_tmpl = env.get_template(subtopic0_tmp)
  prompt0 = prompt0_tmpl.render(subject="Physics", grade="10", board="CBSE", 
                                topic="Light - Reflection and Refraction", 
                                subtopics = concepts["Light - Reflection and Refraction"])
  print(prompt0)
  result0 = call_openai(prompt0)
  result0 = call_openai(prompt0 + "Next Question")
  print(result0)


def answer_multistep(question, prompt0_file, prompt1_file):
  # First get the book/movie type and audience level
  prompt0_tmpl = env.get_template(prompt0_file)
  prompt0 = prompt0_tmpl.render(prev_books=None, question=question)

  # Then use the book/movie type info, inject like information
  if IS_DEBUG: print_debug(prompt0, 0)
  if not IS_MOCK: 
    result0 = call_openai(prompt0)
    print(result0)
    result0 = ast.literal_eval(result0)

    # Now based on book/movie
    # If fiction, then weight by important factors, any user choice, do reweight/normalize
    if result0['type'] == 'physics':
      weights = weight_params['fiction_young']

  # 
  pass
  # Then use the book/movie type info, inject like information
  prompt1_tmpl = env.get_template("prompt1.txt")
  prompt1 = prompt1_tmpl.render(weights=weights, book_name=book_name)

  if IS_DEBUG: print_debug(prompt1, 1)
  if not IS_MOCK: 
    result = call_openai(prompt1, max_tokens=400)
    print(result)

if __name__ == "__main__":
  #prompt_fname = sys.argv[1]
  #question_name = sys.argv[2]
  #print(sys.argv[2])

  #prompt = Path(prompt_fname).read_text()
  #with open(prompt_fname, "rb") as f:
  #    prompt = f.readlines()
  select_subtopics()
