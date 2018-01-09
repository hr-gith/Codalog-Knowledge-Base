import pandas as pd
import matplotlib.pyplot as plt

raw_data = {'File':['clique10.pl', 'Graph10.pl' , 'small.pl'],
            'semiNaive':[1.70252, 0.31603 , 0.031204 ],
             'Naive': [3.90360, 0.36646 , 0.015663 ],
              }

df = pd.DataFrame(raw_data, columns = ['File' , 'semiNaive' , 'Naive'])
print(df)

pos = list(range(len(df['semiNaive'])))
width = 0.15
fig, ax = plt.subplots(figsize=(10,5))


plt.bar(pos, df['semiNaive'], width, alpha = 0.5 , label = df['File'][0] )
plt.bar([p + width for p in pos],
        df['Naive'],
        # of width
        width,
        # with alpha 0.5
        alpha=0.5,
        # with color
        color='#F78F1E',
        # with label the second value in first_name
        label=df['File'][1])

ax.set_ylabel('Time in ms')
ax.set_title('Comparison Between Naive and Semi-Naive')
ax.set_xticks([p + 1.5 * width for p in pos])
ax.set_xticklabels(df['File'])

plt.xlim(min(pos)-width, max(pos)+width*4)
plt.ylim([0, max(df['semiNaive'] + df['Naive'])])
plt.legend(['semiNaive', 'Naive'], loc='upper left')
#plt.grid()
plt.show()



