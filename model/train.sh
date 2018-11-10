#!/bin/bash

mkdir -p model/

python -m nmt.nmt \
    --attention=scaled_luong \
    --src=cs --tgt=en \
    --vocab_prefix=data/vocab.50K  \
    --train_prefix=data/train.small \
    --dev_prefix=data/newstest2013  \
    --test_prefix=data/newstest2015 \
    --out_dir=model/ \
    --num_train_steps=12000 \
    --steps_per_stats=100 \
    --num_layers=2 \
    --num_units=128 \
		--learning_rate=0.001 \
		--optimzer='adam' \
    --dropout=0.2 \
    --metrics=bleu
