import os
import json
from jinja2 import Template, Environment, FileSystemLoader
import openai as oai

from flask import Flask, jsonify, request

app = Flask(__name__)

env = Environment(loader=FileSystemLoader("prompts/"))
env.lstrip_blocks = True
env.trim_blocks = True

oai.api_key = os.getenv("OPENAI_API_KEY")
with open("concepts.json", 'r') as f:
  concepts = json.load(f)
with open("data/topic_graph.json", 'r') as f:
  data = json.load(f)
with open("phy_subtop_qns.json", 'r') as f:
  phy_subtop_qns = json.load(f)
mapping = {"Physics":0, "Chemistry":1, "Maths":2, "Biology":3}

def call_openai(prompt, max_tokens=1000, temp=0.3):
  completion = oai.ChatCompletion.create(model="gpt-3.5-turbo", messages = [{"role":"user", "content":prompt}],
                                           temperature = temp, top_p = 1, n=1, max_tokens=max_tokens)
  return(completion.choices[0].message.content)


@app.route('/get_subtopic_qns')
def get_subtopic_qns():
  board = request.args.get('board')
  grade = request.args.get('grade')
  subject = request.args.get('subject')
  topics = request.args.get('topic')
  topic_ids = request.args.get('topic_id')

  if subject != 'Physics':
      return {'None'}

  results = {k:v for k,v in phy_subtop_qns.items() if k in topic_ids}
  return jsonify(results)



@app.route('/get_subtopic_qn')
def get_subtopic_qn():
  board = request.args.get('board')
  grade = request.args.get('grade')
  subject = request.args.get('subject')
  topic = request.args.get('topic')
  topic_id = request.args.get('topic_id')
  subtopic0_tmp = "subtopics0.txt"
  print(mapping[subject])
  print(topic_id)
  subtopics = data[int(grade)-5]["subjects"][mapping[subject]]["topics"][int(topic_id)]["sub_topics"]
  print(subtopics)
  prompt0_tmpl = env.get_template(subtopic0_tmp)
  prompt0 = prompt0_tmpl.render(subject=subject, grade=grade, board=board,
                                topic=topic, subtopics = subtopics,
                                concepts = concepts[topic])
  print(prompt0)
  question = call_openai(prompt0)
  return jsonify({'status':'in-progress', 'type': 'question', 'question': question})


@app.route('/ping')
def ping():
    return 'Pong!'

if __name__ == '__main__':
    app.run()
