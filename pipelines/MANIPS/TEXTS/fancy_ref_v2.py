from typing import List

class Pipeline:

    def __init__(self):
        pass

    def __call__(self, 
                 metadata : dict,
                 text : List[str],
                 ) -> str:
        texts = [t for x in text for t in x.split('STOP') if t]
        num = metadata["num"]
        try:
            year,month,_ = metadata["publication_date"].split('-')
            month_names = {'01':'January',
                        '02':'February',
                        '03':'March',
                        '04':'April',
                        '05':'May',
                        '06':'June',
                        '07':'July',
                        '08':'August',
                        '09':'September',
                        '10':'October',
                        '11':'November',
                        '12':'December'}
            month = month_names[month]
            prefix = f"[{num}] ({month} {year})"
        except:
            prefix = f"[{num}]"
        return '\n'.join([f"{prefix} {t.strip()}" for t in texts if t.strip()])
    

        