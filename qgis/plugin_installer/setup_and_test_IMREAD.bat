python -m venv --system-site-packages venv
call "venv\Scripts\activate.bat"
pip install --upgrade setuptools wheel
pip install -r requirements.txt
ipython -c "from imread import imread; im = imread('lena.jpg'); print(im.shape,im[0,0])"
PAUSE

