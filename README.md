# forestplot
Python script to create forest plots

## Installation

```
git clone https://github.com/NicolasLoiseau/forestplot.git
cd forestplot/
pip install -e .
```

## Example

```
from forestplot.plot import plot
from forestplot.utils import analyse

df = your pandas dataset
trt, T, E = 'treatment name', 'time name', 'event name'
data = analyse(df, trt, T, E, dropna=False)
plot(data, savepath='forestplot.png')
```