#!/bin/bash

mkdir -p model/

python -m nmt.nmt \
    --src=cs --tgt=en \
    --vocab_prefix=/tmp/nmt_data/vocab.10K  \
    --train_prefix=/tmp/nmt_data/train.small \
    --dev_prefix=data/newstest2013  \
    --test_prefix=data/newstest2015 \
    --out_dir=/tmp/nmt_model/ \
    --num_train_steps=2000 \
    --steps_per_stats=50 \
    --num_layers=4 \
    --num_units=256 \
		--learning_rate=0.001 \
		--optimzer='adam' \
    --dropout=0.2 \
    --metrics=bleu
