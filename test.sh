#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Server and Cleanup functions ---
start_server() {
    echo "Starting local HTTP server for scraping test..."
    python3 -m http.server 8000 &
    server_pid=$!
    sleep 2
}

cleanup() {
    echo -e "\n--- Cleaning up test environment ---"
    if [ ! -z "$server_pid" ]; then
        if ps -p $server_pid > /dev/null; then
           echo "Stopping local HTTP server (PID: $server_pid)..."
           kill $server_pid
        fi
    fi
    rm -f common_test.txt test_page_*.html test_output.txt
}

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

cat > common_test.txt << EOL
password
123456
admin
EOL

cat > test_page_1.html << EOL
<html><body><h1>Page One</h1><p>words: alpha bravo</p><a href="test_page_2.html">Link to Page 2</a><a href="http://externalsite.com">External Link</a></body></html>
EOL

cat > test_page_2.html << EOL
<html><body><h1>Page Two</h1><p>words: charlie delta</p><a href="test_page_1.html">Link back to Page 1</a></body></html>
EOL

# --- Test Cases ---

echo -e "\n--- Running Test Cases ---"

# Make the script executable first
chmod +x wordlist_generator.py

# 1. Basic generation
output=$(./wordlist_generator.py --min-length=2 --max-length=2 --charset="12")
expected_output=$'11\n12\n21\n22'
assert_equal "$expected_output" "$output" "Basic generation"

# 2. File output
./wordlist_generator.py --min-length=1 --max-length=1 --charset="a" -o test_output.txt
file_content=$(cat test_output.txt)
assert_equal $'a' "$file_content" "File output (-o)"

# 3. Common list inclusion
output=$(./wordlist_generator.py --common-list=common_test.txt)
expected_output=$'password\n123456\nadmin'
assert_equal "$expected_output" "$output" "Common list inclusion"

# 4. Web Scraping Tests
echo "Installing dependencies for scraping test..."
pip install -r requirements.txt > /dev/null 2>&1
start_server
url1="http://localhost:8000/test_page_1.html"
echo "Testing non-recursive scrape..."
output_non_recursive=$(./wordlist_generator.py --url="$url1")
expected_non_recursive=$'2\nalpha\nbravo\nexternal\nlink\none\npage\nto\nwords'
assert_equal "$expected_non_recursive" "$output_non_recursive" "Web scraping (non-recursive)"
echo "Testing recursive scrape (depth=2)..."
output_recursive=$(./wordlist_generator.py --url="$url1" --recursive --depth=2)
expected_recursive=$'1\n2\nalpha\nback\nbravo\ncharlie\ndelta\nexternal\nlink\none\npage\nto\ntwo\nwords'
assert_equal "$expected_recursive" "$output_recursive" "Web scraping (recursive, depth=2)"

# 5. Combined common list and generation
output=$(./wordlist_generator.py --common-list=common_test.txt --min-length=1 --max-length=1 --charset="z")
expected_output=$'password\n123456\nadmin\nz'
assert_equal "$expected_output" "$output" "Combined common list and generation"

# 6. Error handling (min > max)
if ./wordlist_generator.py --min-length=3 --max-length=2 --numeric > /dev/null 2>&1; then
    echo "❌ FAILED: Error handling (min > max)"
    exit 1
else
    echo "✅ PASSED: Error handling (min > max)"
fi

# 7. Prefix and suffix formatting
output=$(./wordlist_generator.py --min-length=1 --max-length=1 --charset="a" --prefix="pre-" --suffix="-post")
expected_output=$'pre-a-post'
assert_equal "$expected_output" "$output" "Prefix and suffix formatting"

# 8. Progress bar
echo "Installing dependencies for progress bar test..."
pip install tqdm > /dev/null 2>&1
stderr_output=$(./wordlist_generator.py --min-length=2 --max-length=2 --charset="ab" --progress 2>&1 >/dev/null)
stdout_output=$(./wordlist_generator.py --min-length=2 --max-length=2 --charset="ab" --progress)
expected_stdout=$'aa\nab\nba\nbb'
assert_equal "$expected_stdout" "$stdout_output" "Progress bar (stdout)"
if echo "$stderr_output" | grep -q "100%"; then
    echo "✅ PASSED: Progress bar (stderr)"
else
    echo "❌ FAILED: Progress bar (stderr)"
    echo "   Stderr was: '$stderr_output'"
    exit 1
fi

# 9. Pattern generation
output=$(./wordlist_generator.py --pattern="a?d")
expected_output=$'a0\na1\na2\na3\na4\na5\na6\na7\na8\na9'
assert_equal "$expected_output" "$output" "Pattern generation"

# 10. Pattern and charset mode mutual exclusion
if ./wordlist_generator.py --pattern="a?d" --min-length=2 > /dev/null 2>&1; then
    echo "❌ FAILED: Error handling (pattern and charset mode)"
    exit 1
else
    echo "✅ PASSED: Error handling (pattern and charset mode)"
fi

echo -e "\n🎉 All tests passed successfully! 🎉"
