(find mangareader -name "*tests.py" -print0 | xargs -0 -n1 python && echo "All Tests Passed") || echo "Something went wrong"
