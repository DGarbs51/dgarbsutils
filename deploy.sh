cd ~/code/opensource/py-utils
python3 -m build
python3 -m twine upload --repository pypi dist/*
python3 -m twine upload --repository nexus dist/*
pip install dgarbsutils --upgrade
rm -rf deploy
pip install --target="deploy/python" dgarbsutils
cd deploy
zip -r python.zip python
#python3 /home/ec2-user/code/cicd-infrastructure/init/get-token/saml_get_token.py both
