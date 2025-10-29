#!/bin/bash
set -e

INPUT_IMAGE="/output/page-11.png"
OUTPUT_DIR="/output"

convert "$INPUT_IMAGE" -crop 800x600+200+300 "${OUTPUT_DIR}/page-11-christmas-eve-in-millers-point.png"
convert "$INPUT_IMAGE" -crop 800x600+1400+300 "${OUTPUT_DIR}/page-11-the-code.png"
convert "$INPUT_IMAGE" -crop 800x600+2600+300 "${OUTPUT_DIR}/page-11-east-of-noon.png"
convert "$INPUT_IMAGE" -crop 800x600+3800+300 "${OUTPUT_DIR}/page-11-the-editorial-office.png"
convert "$INPUT_IMAGE" -crop 800x600+200+1600 "${OUTPUT_DIR}/page-11-conclave.png"
convert "$INPUT_IMAGE" -crop 800x600+1400+1600 "${OUTPUT_DIR}/page-11-dont-cry-butterfly.png"
convert "$INPUT_IMAGE" -crop 800x600+2600+1600 "${OUTPUT_DIR}/page-11-the-fable.png"
convert "$INPUT_IMAGE" -crop 800x600+3800+1600 "${OUTPUT_DIR}/page-11-familiar-touch.png"
