#!/bin/bash

python -m nmt.nmt \
    --out_dir=model/ \
    --inference_input_file=input \
    --inference_output_file=output
