import pandas as pd

NAME_KEY = 'Unnamed: 0'
END_KEY = '┤'

if __name__ == '__main__':
    with open('resource/first_set.html') as f:
        html_str = f.read()

    dfs = pd.read_html(html_str)
    df = dfs[0]
    set_dict = {}

    for i in range(len(df)):
        set_dict[df.iloc[i][NAME_KEY]] = []
        if df.iloc[i][END_KEY] == '+':
            set_dict[df.iloc[i][NAME_KEY]].append('$')
        for j in list(df.keys()):
            if j == NAME_KEY or j == END_KEY:
                continue
            if df.iloc[i][j] == '+':
                set_dict[df.iloc[i][NAME_KEY]].append(j)

    print(set_dict)
