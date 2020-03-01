#define external javascripts, css and meta_tags to included

external_scripts = [
    {
       'href': 'https://code.jquery.com/jquery-3.3.1.slim.min.js',
       'crossorgin': 'anonymous',
       'integrity': 'sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo'
    },
    {
       'href': 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js',
       'crossorgin': 'anonymous',
       'integrity': 'sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1'
    },
    {
       'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js',
       'crossorgin': 'anonymous',
       'integrity': 'sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM',
    }
]


external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    },
    #'https://codepen.io/chriddyp/pen/brPBPO.css'
]

meta_tags = [
              {'charset':'UTF-8'},
              {'http-equiv':"X-UA-Compatible", 'conent':"IE=edge"},
              {'name': 'viewport', 'content':  "width=750, initial-scale=1.0, shrink-to-fit=yes"}
             ]#device-width

