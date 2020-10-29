#!/bin/bash

set -e

MODEL=models/contact_form.json
GEN_STOP_COND="random(vertex_coverage(100) and edge_coverage(100))"
#GEN_STOP_COND="random(vertex_coverage(100) and edge_coverage(100) and time_duration(30))"
TESTS_DIR=tests
altwalker check -m $MODEL "$GEN_STOP_COND"
altwalker verify -m $MODEL $TESTS_DIR
altwalker online tests -m $MODEL "$GEN_STOP_COND"

