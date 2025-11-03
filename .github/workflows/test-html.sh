#!/bin/bash

# Script to test basic HTML structure and content
# Tests are based on the requirements:
# - Site header contains "LIFF Archive" logo
# - Main page exists and has expected content
# - About page exists and has expected content

PUBLIC_DIR="hugo/public"
FAILED=0

echo "Running HTML validation tests..."
echo "================================="

# Helper function to check if a file contains a string
check_content() {
    local file=$1
    local search_string=$2
    local description=$3
    
    if [ ! -f "$file" ]; then
        echo "❌ FAIL: $description - File $file does not exist"
        FAILED=1
        return 1
    fi
    
    if grep -q "$search_string" "$file"; then
        echo "✅ PASS: $description"
        return 0
    else
        echo "❌ FAIL: $description - String '$search_string' not found in $file"
        FAILED=1
        return 1
    fi
}

# Test 1: Check main page exists
echo ""
echo "Test 1: Main page exists"
check_content "$PUBLIC_DIR/index.html" "<html" "Main page (index.html) exists and is valid HTML"

# Test 2: Check site header in main page
echo ""
echo "Test 2: Site header in main page"
check_content "$PUBLIC_DIR/index.html" "LIFF Archive" "Main page contains site header with 'LIFF Archive'"

# Test 3: Check main page has expected content
echo ""
echo "Test 3: Main page content"
check_content "$PUBLIC_DIR/index.html" "This site is an archive of films shown at the Leeds International Film Festival" "Main page contains expected introductory text"

# Test 4: Check about page exists
echo ""
echo "Test 4: About page exists"
check_content "$PUBLIC_DIR/about/index.html" "<html" "About page exists and is valid HTML"

# Test 5: Check site header in about page
echo ""
echo "Test 5: Site header in about page"
check_content "$PUBLIC_DIR/about/index.html" "LIFF Archive" "About page contains site header with 'LIFF Archive'"

# Test 6: Check about page has expected content
echo ""
echo "Test 6: About page content"
check_content "$PUBLIC_DIR/about/index.html" "Getting the data" "About page contains 'Getting the data' section"
check_content "$PUBLIC_DIR/about/index.html" "Building the site" "About page contains 'Building the site' section"

# Test 7: Check navigation menu exists
echo ""
echo "Test 7: Navigation menu"
check_content "$PUBLIC_DIR/index.html" "By Year" "Main page has navigation menu with 'By Year'"
check_content "$PUBLIC_DIR/index.html" "By Strand" "Main page has navigation menu with 'By Strand'"
check_content "$PUBLIC_DIR/index.html" "By Title" "Main page has navigation menu with 'By Title'"

echo ""
echo "================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed!"
    exit 1
fi
