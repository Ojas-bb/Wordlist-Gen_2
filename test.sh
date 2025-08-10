#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Server and Cleanup functions ---
start_server() {
    echo "Starting local HTTP server for scraping test..."
    python3 -m http.server 8000 &
    server_pid=$!
    # Wait for server to start
    sleep 2
}

cleanup() {
    echo -e "\n--- Cleaning up test environment ---"
    if [ ! -z "$server_pid" ]; then
        echo "Stopping local HTTP server (PID: $server_pid)..."
        kill $server_pid
    fi
    rm -f common_test.txt test.html test_output.txt
}

# Trap to ensure cleanup runs on exit
trap cleanup EXIT

# --- Helper Functions ---
assert_equal() {
    local expected="$1"
    local actual="$2"
    local message="$3"
    if [ "$expected" == "$actual" ]; then
        echo "✅ PASSED: $message"
    else
        echo "❌ FAILED: $message"
        echo "   Expected: '$expected'"
        echo "   Actual:   '$actual'"
        exit 1
    fi
}

# --- Test Setup ---
echo "Setting up test environment..."

# Create a dummy common password list
cat > common_test.txt << EOL
password
123456
admin
EOL

# Create a dummy HTML file for testing web scraping
cat > test.html << EOL
<html>
<head><title>Test Page</title></head>
<body>
    <h1>Hello World</h1>
    <p>This is a test page with some words: apple, banana, apple, cherry.</p>
    <p>And some numbers 123 and symbols !@#$.</p>
    <script>var x = "ignore me";</script>
</body>
</html>
EOL

# --- Test Cases ---

echo -e "\n--- Running Test Cases ---"

# 1. Test basic generation (2-char from '12')
output=$(./wordlist_generator.py --min-length 2 --max-length 2 --charset "12")
expected_output=$'11\n12\n21\n22'
assert_equal "$expected_output" "$output" "Basic generation"

# 2. Test file output
./wordlist_generator.py --min-length 1 --max-length 1 --charset "a" -o test_output.txt
file_content=$(cat test_output.txt)
assert_equal $'a' "$file_content" "File output (-o)"

# 3. Test common list inclusion
output=$(./wordlist_generator.py --common-list common_test.txt)
expected_output=$(cat common_test.txt)
assert_equal "$expected_output" "$output" "Common list inclusion"

# 4. Test web scraping from local file
# Need to install dependencies first for this test
echo "Installing dependencies for scraping test..."
pip install -r requirements.txt > /dev/null 2>&1

start_server

http_url="http://localhost:8000/test.html"
output=$(./wordlist_generator.py --url "$http_url")
expected_output=$'123\na\nand\napple\nbanana\ncherry\nhello\nis\nnumbers\npage\nsome\nsymbols\ntest\nthis\nwith\nwords\nworld'
assert_equal "$expected_output" "$output" "Web scraping from local HTTP server"

# 5. Test combined common list and generation
output=$(./wordlist_generator.py --common-list common_test.txt --min-length 1 --max-length 1 --charset "z")
expected_output=$'password\n123456\nadmin\nz'
assert_equal "$expected_output" "$output" "Combined common list and generation"

# 6. Test error case: min_length > max_length
if ./wordlist_generator.py --min-length 3 --max-length 2 --numeric > /dev/null 2>&1; then
    echo "❌ FAILED: Error handling (min > max)"
    exit 1
else
    echo "✅ PASSED: Error handling (min > max)"
fi

echo -e "\n🎉 All tests passed successfully! 🎉"
