echo "Update setup.py with modules to publish"
read ok
echo "Update setup.py with required packages"
read ok
echo "Update setup.py with version number and download url"
read ok
echo "Push latest to github"
read ok
echo "Create release on github"
read ok
echo "Running setup.py"
python setup.py sdist
echo "Running twine"
twine upload dist/*.*