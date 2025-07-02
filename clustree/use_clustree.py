from sklearn import datasets
import pandas as pd
from clustree import clustree
from sklearn.cluster import KMeans

data = datasets.load_iris()
X = data.data[:, :2]
y = data.target

data_final = pd.DataFrame()


for k in range(1, 24):
    km = KMeans(
        n_clusters=k, init='random',
        n_init=10, max_iter=300,
        tol=1e-04, random_state=0
    )
    y_km = km.fit_predict(X=X, y=y)
    col = "K" + str(k)
    data_final[col]=y_km

print(data_final.head())

ct = clustree(data=data_final,
              prefix="K",
              draw=True,
              output_path="C:\\Users\\G\\PycharmProjects\\S_T_Error\\ClusTree",
              images="C:\\Users\\G\\PycharmProjects\\S_T_Error\\ClusTree")