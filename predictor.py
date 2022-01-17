"""
    Copyright 2021 t.me/hikariakami
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

#<3 title: Predictor
#<3 pic: https://img.icons8.com/fluency/48/000000/voice-id.png
#<3 desc: Угадывает, отправлено ли сообщение юзерботом, или нет.

from .. import loader, utils, main
import logging
import threading
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from copy import deepcopy
from sklearn.model_selection import train_test_split
import re
import asyncio
import requests
import telethon

import emoji

logger = logging.getLogger('Predictor')


def is_emoji(s):
    return bool(emoji.get_emoji_regexp().search(s))


def startswithemoji(s):
    return bool(emoji.get_emoji_regexp().search(s[0]))


def has_digits(s):
    return any(str(i) in s for i in range(10))


clf = None


def train():
    global clf
    logger.info('Started training')

    open('documents.txt', 'w').write(requests.get('https://x0.at/Z1xe.txt').text)

    np.random.seed(0)

    df = pd.read_csv('documents.txt', sep='\t').drop(columns=['from_id'])
    df['has_emojies'] = df.text.apply(is_emoji)
    df['start_with_emoji'] = df.text.apply(startswithemoji)
    df['has_digits'] = df.text.str.contains('\\d', regex=True)
    df['has_link'] = df.text.str.contains('http://') | df.text.str.contains('https://')
    df['ru_count'] = df.text.str.count('[а-яА-Я]')
    df['en_count'] = df.text.str.count('[a-zA-Z]')
    df['spec_count'] = df.text.str.count(r'[!#$%&\'()*+,./:;<=>?@[\]^_{|}~—\"\-]')
    df['n_words'] = df.text.str.count(' ') + 1
    inp = df.drop(columns=['text'])
    X, y = inp.drop(columns=['type']), inp['type']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    clf = RandomForestClassifier(criterion='entropy', random_state=0)
    search = RandomizedSearchCV(clf, {
        'n_estimators': range(1, 20),
        'max_depth': range(1, 20),
        'min_samples_split': range(2, 20),
        'min_samples_leaf': range(2, 20)
    })

    search.fit(X_train, y_train)
    clf = search.best_estimator_
    logger.info(f'Picked params for tree {search.best_params_}')
    logger.info('Testing params on tree')
    res = clf.score(X_test, y_test)
    logger.info(f'{res}')



def normalize(text, entities_q=0, from_id=0):
        return pd.DataFrame({
            'entities_q': entities_q,
            'has_emojies': [is_emoji(text)],
            'start_with_emoji': [startswithemoji(text)],
            'has_digits': [has_digits(text)],
            'has_link': [('http://' in text or 'https://' in text)],
            'ru_count': [len(re.findall('[а-яА-Я]', text))],
            'en_count': [len(re.findall('[a-zA-Z]', text))],
            'spec_count': [len(re.findall(r'[!#$%&\'()*+,./:;<=>?@[\]^_{|}~—\"\-]', text))],
            'n_words': [text.count(' ') + 1]
        })


def predict(text, entities_q=0, from_id=0, threshold=.7):
    normalized = normalize(text, entities_q, from_id)
    d = normalized.to_dict()
    r = {i: v[0] for i, v in d.items()}
    # logger.info(r)
    probability = clf.predict_proba(normalized)
    if probability[0][0] > threshold:
        return True, round(probability[0][0], 5) * 100 # Bot
    return False, round(probability[0][1], 5) * 100 # Human


db = open('/home/ftg/df.txt', 'r').read()


@loader.tds
class PredictorMod(loader.Module):
    """No Description"""
    strings = {
        "name": "Predictor",
        "bot": "🤖 <b>Pretty sure it's userbot ({}%)</b>",
        "human": "🧙‍♂️ <b>Pretty sure it's human ({}%)</b>"
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        await utils.run_sync(train)

    async def isbotcmd(self, message):
        reply = await message.get_reply_message()
        ent = len(reply.entities) if reply.entities is not None else 0
        res = predict(reply.raw_text, ent, reply.sender_id)
        await utils.answer(message, self.strings('bot' if res[0] else 'human').format(res[1]))

    async def watcher(self, message):
        # try:
        global db
        if not message.is_group: return
        if message.raw_text is None: return
        if message.out: return
        await asyncio.sleep(1)
        message = (await self.client.get_messages(message.peer_id, offset_id=message.id - 1, limit=1, reverse=True))[0]
        text = message.raw_text.replace('\n', ' N')
        if text.count(' ') < 2: return
        ent = len(message.entities) if message.entities is not None else 0
        predicted = predict(text, ent, message.sender_id)
        classified = 'bot' if predicted[0] else 'human'
        logger.info(f"{text} ==> {predicted}")
        filling = f"{classified}\t{text}\t{ent}\t{message.sender_id}\n"
        db += filling
        open('/home/ftg/df.txt', 'w').write(db)

        if not predicted[0]:
            return

        try:
            await self.client(telethon.functions.messages.SendReactionRequest(message.peer_id, message.id, '👍'))
        except Exception:
            pass
        
