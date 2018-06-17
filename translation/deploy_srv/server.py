#!/usr/bin/env python

import argparse
from flask import Flask, jsonify, request
import torch
from torch import nn
from torch.nn import functional as F
import sys
sys.path.insert(0, '../nmt_train/')
from data_utils import prepare_data, unicode_to_ascii, normalize_string
from train import EncoderRNN, AttnDecoderRNN, evaluate



STATUS_OK = "ok"
STATUS_ERROR = "error"
app = Flask(__name__)
host="0.0.0.0"
port=5000
debug = True
MAX_LENGTH=30
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@app.route('/translate', methods=['POST'])
def translate():

    data = request.get_json(force=True)
    message = data['src']
    message_normalized = unicode_to_ascii(message)
    message_normalized = normalize_string(message)
    if data['direction'] == 0: # en-fi
        translation = evaluate(encoder_en_fi, attn_decoder_en_fi, message_normalized, en_lang, fi_lang)
    else:
        translation = evaluate(encoder_fi_en, attn_decoder_fi_en, message_normalized, fi_lang, en_lang)

    return jsonify({"src":message, 'tgt':' '.join(translation[0][:-1])})


if __name__ == "__main__":
    global fi_lang, en_lang
    global encoder_fi_en, attn_decoder_fi_en
    global encoder_en_fi, attn_decoder_en_fi

    en_lang, fi_lang, _ = prepare_data('fin', 'en', reverse=False, main_dir='../nmt_train')

    #Network parameters
    # Finnish -> English

    # Due to the previous bugs, I have make a trakc - swapt the models
    hidden_size = 512
    encoder_fi_en = EncoderRNN(fi_lang.n_words, hidden_size).to(device)
    attn_decoder_fi_en = AttnDecoderRNN(hidden_size, en_lang.n_words, dropout_p=0.1).to(device)
    encoder_fi_en.load_state_dict(torch.load('../nmt_train/encoder_eng_fin.pt'))
    attn_decoder_fi_en.load_state_dict(torch.load('../nmt_train/decoder_eng_fin.pt'))
    encoder_fi_en.to("cuda")
    attn_decoder_fi_en.to("cuda")
    # English -> Finnish
    encoder_en_fi = EncoderRNN(en_lang.n_words, hidden_size).to(device)
    attn_decoder_en_fi = AttnDecoderRNN(hidden_size, fi_lang.n_words, dropout_p=0.1).to(device)
    encoder_en_fi.load_state_dict(torch.load('../nmt_train/encoder_fin_eng.pt'))
    attn_decoder_en_fi.load_state_dict(torch.load('../nmt_train/decoder_fin_eng.pt'))
    encoder_en_fi.to("cuda")
    attn_decoder_en_fi.to("cuda")

    app.run(debug=debug, host=host, port=port, use_reloader=False)