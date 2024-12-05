import pandas as pd
import torch

filename = 'test.csv'
df = pd.read_csv(filename)
# df = pd.DataFrame([1,2])
df_list = df.values.tolist()
print(df_list)
df_tensor = torch.tensor(df_list)
print(df_tensor.shape)
