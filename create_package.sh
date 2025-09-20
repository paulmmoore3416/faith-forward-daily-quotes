#!/bin/bash
# Faith Forward Planner - Package Creator
# Creates a distributable package of the Faith Forward Planner

echo "=== Faith Forward Planner Package Creator ==="
echo "Spiritus Invictus - The Unconquered Spirit"
echo ""

# Create package directory
PACKAGE_NAME="faith-forward-planner-v1.0"
PACKAGE_DIR="/tmp/$PACKAGE_NAME"

echo "Creating package directory: $PACKAGE_DIR"
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy all necessary files
echo "Copying application files..."
cp -r faith_forward_planner/* "$PACKAGE_DIR/"

# Create installation package
echo "Creating installation package..."
cd /tmp
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

echo ""
echo "=== Package Created Successfully! ==="
echo ""
echo "Package location: /tmp/$PACKAGE_NAME.tar.gz"
echo "Package size: $(du -h /tmp/$PACKAGE_NAME.tar.gz | cut -f1)"
echo ""
echo "To install:"
echo "1. Extract: tar -xzf $PACKAGE_NAME.tar.gz"
echo "2. cd $PACKAGE_NAME"
echo "3. ./install.sh"
echo ""
echo "To test without installation:"
echo "1. Extract package"
echo "2. cd $PACKAGE_NAME"
echo "3. python3 demo.py"
echo ""
echo "Spiritus Invictus!"