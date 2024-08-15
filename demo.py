import datetime
from dateutil import parser
import gradio as gr
import pickle
import os
import json
from openai import OpenAI


OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

MAPPING = {
    '인사동': './res/reviews.json',
    '판교': './res/ninetree_pangyo.json',
    '용산': './res/ninetree_yongsan.json'
}

with open('./res/prompt_1shot.pickle', 'rb') as f:
    PROMPT = pickle.load(f)

def preprocess_reviews(path='./res/reviews.json'):
    # json 불러오기
    with open(path, 'r', encoding='utf-8') as f:
        review_list = json.load(f)

    reviews_good, reviews_bad = [], []
    
    current_date = datetime.datetime.now() # 현재 날짜
    date_boundary = current_date - datetime.timedelta(days=6*30) # 6 month

    for r in review_list:
        review_date_str = r['date']
        try:
            review_date = parser.parse(review_date_str)
        except (ValueError, TypeError): # 6시간 전, 22시간 전 등 에러
            review_date = current_date # 지금 날짜

        # 리뷰 날짜가 6개월안에 속하면, 계속
        if review_date < date_boundary:
            continue

        if r['stars'] == 5: # special token 'REVIEW_START', 'REVIEW_END'
            reviews_good.append('[REVIEW_START]' + r['review'] + '[REVIEW_END]')
        else:
            reviews_bad.append('[REVIEW_START]' + r['review'] + '[REVIEW_END]')
    # LIST -> TEXT로 바꿔주기
    reviews_good_text = '\n'.join(reviews_good)
    reviews_bad_text = '\n'.join(reviews_bad)

    return reviews_good_text, reviews_bad_text

def summarize(reviews):
    prompt = PROMPT + '\n\n' + reviews

    client = OpenAI(api_key=OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model='gpt-3.5-turbo-0125',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.0
    )
    return completion

def fn(accom_name):
    path = MAPPING[accom_name]
    reviews_good, reviews_bad = preprocess_reviews(path) 
    
    summary_good = summarize(reviews_good).choices[0].message.content
    summary_bad = summarize(reviews_bad).choices[0].message.content

    return summary_good, summary_bad

def run_demo():
    demo = gr.Interface(
        fn = fn,
        inputs = [gr.Radio(['인사동', '판교', '용산'], label='숙소')],
        outputs = [gr.Textbox(label='높은 평점 요약'), gr.Textbox(label='낮은 평점 요약')]
    )
    demo.launch(share=True) # share=True : 로컬 URL 72시간동안 유효

if __name__ == '__main__':
    run_demo()