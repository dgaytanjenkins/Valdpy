#!/bin/bash
# Quick setup and push to GitHub

echo "🚀 VALDPY GitHub Push Guide"
echo "=============================="
echo ""

echo "1. Verify your GitHub credentials are set up:"
echo "   git config --global user.name 'Your Name'"
echo "   git config --global user.email 'your@email.com'"
echo ""

echo "2. Navigate to the project directory:"
echo "   cd c:\Users\dgaytanj\Documents\automate_boring_stuff\vald\prod"
echo ""

echo "3. Check the current status:"
echo "   git status"
echo ""

echo "4. Verify remote repository is set correctly:"
echo "   git remote -v"
echo "   Expected: git@github.com:dgaytanjenkins/Valdpy.git"
echo ""

echo "5. Push to GitHub:"
echo "   git push origin main"
echo ""

echo "6. If push is rejected, pull first:"
echo "   git pull origin main"
echo "   git push origin main"
echo ""

echo "7. Verify on GitHub:"
echo "   https://github.com/dgaytanjenkins/Valdpy"
echo ""

echo "✅ Once pushed, your package is ready for:"
echo "   - Installing from GitHub: pip install git+https://github.com/dgaytanjenkins/Valdpy.git"
echo "   - Publishing to PyPI: python setup.py sdist bdist_wheel && twine upload dist/*"
echo "   - Creating releases and tags"
echo ""

echo "📚 Documentation:"
echo "   - README.md - Main project documentation"
echo "   - docs/getting_started.md - Installation & setup"
echo "   - CONTRIBUTING.md - For contributors"
echo "   - CHANGELOG.md - Version history"
