#!/bin/bash

set -e

MODEL1=models/contact_form.json
MODEL2=models/message_backoffice.json
GEN_STOP_COND="random(vertex_coverage(100) and edge_coverage(100))"
TESTS_DIR=tests
altwalker check -m $MODEL1 "$GEN_STOP_COND"
altwalker check -m $MODEL2 "$GEN_STOP_COND"
altwalker verify -m $MODEL2 $TESTS_DIR
altwalker verify -m $MODEL2 $TESTS_DIR
altwalker online tests -m $MODEL1 "$GEN_STOP_COND" -m $MODEL2 "$GEN_STOP_COND"

