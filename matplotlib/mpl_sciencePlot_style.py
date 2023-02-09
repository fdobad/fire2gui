import matplotlib.pyplot as plt
import numpy as np
import scienceplots
plt.style.use('science')

# Data for plotting
t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)
fig, ax = plt.subplots()
ax.plot(t, s)
ax.set(xlabel='time (s)', ylabel='voltage (mV)',
       title='About as simple as it gets, folks')
ax.grid()
fig.savefig("test.png")
plt.tight_layout()
plt.show()

'''
pip install sciencePlot
sudo apt-get install dvipng texlive-latex-extra texlive-fonts-recommended cm-super
sudo apt update
sudo apt install fonts-noto-cjk

https://pypi.org/project/SciencePlots/
https://github.com/garrettj403/SciencePlots/wiki/FAQ#installing-latex
https://github.com/garrettj403/SciencePlots/wiki/FAQ#installing-cjk-fonts
https://github.com/garrettj403/SciencePlots/
'''

