#!/bin/bash
for i in {1..8}; do
    echo "========================================="
    echo "RUNNING ITERATION $i"
    echo "========================================="
    coverage erase
    coverage run --branch -m unittest tests_iteration_$i.py
    coverage report -m
    coverage html
    mv htmlcov htmlcov_iteration_$i
    echo ""
done
