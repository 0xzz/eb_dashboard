import dash_html_components as html

def get_intro():
    return html.Div([
        html.H6([
            'Visit us',
            html.A('New Immigrants United', href='http://www.niunational.org/',className='external_links', style={'font-size':'1.6rem'},target='_blank'),
        ]),
            # NIU  ',style={'Display':'inline-block'}),
        html.H6('Join our discussion on Telegram 来电报群讨论吧'),
        html.A('美国绿卡排期分析电报群', href='https://t.me/EBGreenCard',className='external_links',target='_blank'),
        html.A('美国EB1绿卡申请互助电报群  ', href='http://t.me/EB1GC',className='external_links',target='_blank'),
        html.A('美国EB23绿卡申请互助电报群  ', href='http://t.me/usaeb12345',className='external_links',target='_blank'),
        html.A('中国EB5互助群  ', href='https://t.me/EB5CN',className='external_links',target='_blank'),
        html.A('移民数据频道  ', href='https://t.me/ImmigrationData',className='external_links',target='_blank'),
        # html.H6('More Telegram groups 更多电报群推荐'),
        html.A('北美数据科学机器学习群  ', href='https://t.me/dsmldl',className='external_links',target='_blank'),
        # html.A('美股与AI，CS  ', href='https://t.me/USstockXC',className='external_links',target='_blank'),
        # html.A('北美程序员大群  ', href='https://t.me/faangbbs',className='external_links',target='_blank'),
        # html.A('美国华人网华人闲话聊天群  ', href='https://t.me/joinchat/PyOzTUgC1gIlw2AjmuiqTQ',className='external_links',target='_blank'),
        # html.A('美国华人抗冠状病毒群', href='https://t.me/FightSARI',className='external_links',target='_blank'),
        # html.A('加拿大抗肺炎病毒群  ', href='https://t.me/joinchat/QOAsG1NKlAVZhCca6UzMvA',className='external_links',target='_blank'),
        html.P(''' Please note that Some figures might not be displayed properly on small screens. 
If you have some difficulties in viewing all the content of some figures, please swith your browser to desktop mode. 
Sorry for the inconvenience.
''')
    ])
