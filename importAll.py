import os
import time

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler

from sklearn.decomposition import PCA, IncrementalPCA

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from tkinter import Tk
from tkinter import filedialog


from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier as kNN
from sklearn.ensemble import BaggingClassifier
