class Pipeline:
    def __init__(self):
        pass 

    def __call__(self, markdown : str) -> dict:
        y = [_ for _ in markdown.split('\n') if _.count('|') > 1 and len(_.replace('|','').replace(' ','').replace('-','')) >0]
        if len(y) <=1:
            return {}
        columns = [_.strip() for _ in y[0].split('|') if _.strip()][1:]
        rows = [[_.strip() for _ in z.split('|')][1:-1]  for z in  y[1:]]
        parsed =  {k:{} for k in columns}
        try:
            for row in rows:
                row_name = row[0]
                for value, key in zip(row[1:], columns):
                    if value.lower() in {'', 'null', 'not found', 'none', 'absent'}:
                        continue
                    parsed[key][row_name] = value
            return parsed
        except:
            return {}